from django.contrib import messages
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

from string import Template
from models import Service, Issue, Bounty
from django.contrib.auth.models import User
from django.db.models import Sum
from urlparse import urlparse
import urllib
from BeautifulSoup import BeautifulSoup
import base64
import cookielib
import datetime
import re
#from django.utils 
import json
from django.db.models import Count

import urllib2
import requests

def find_api_url(url):
    parsed_url = urlparse(url)
    path_and_query = parsed_url.path+"?"+parsed_url.query
    netloc = parsed_url.netloc
    service = Service.objects.get(domain=netloc)
    template = Template(service.template)
    regex = re.compile(service.regex)
    r = regex.search(path_and_query)
    replaced_url = service.api_url+template.substitute(r.groupdict())
    return replaced_url

def leaderboard():
        return User.objects.filter(userprofile__balance__gt=0).order_by('-userprofile__balance')
    
def get_issue(request, url):
    parsed_url = urlparse(url)
    path_and_query = parsed_url.path+"?"+parsed_url.query
    netloc = parsed_url.netloc
    try:
        service = Service.objects.get(domain=netloc)
    except:
        error = "Please enter a Github, Google Code or Bitbucket issue"
        if not request:
            return error
        messages.error(request, error)
        return False
    template = Template(service.template)
    regex = re.compile(service.regex)
    r = regex.search(path_and_query)
    try:
        replaced_url = service.api_url+template.substitute(r.groupdict())
    except Exception:
        error = "I'm sorry, I couldn't find that "+service.name+" issue."
        if not request:
            return error
        messages.error(request, error)
        return False
    data = r.groupdict()
    req = urllib2.Request(replaced_url, None, {'Content-Type': 'application/' + service.type})
    if service.name == "Bitbucket":
        try:
            result = json.load(urllib2.urlopen(req))
        except Exception, e:
            error = "I wasn't able to retrieve "+data['user']+" / "+data['project']+" issue #"+data['number']
            if not request:
                return error
            messages.error(request, error)
            return False

        data['status'] = (result['status'] == "new" or result['status'] == "open") and "open" or "closed"
        data['title'] = result['title']
        data['content'] = result['content']
        data['service'] = service.name

    elif service.name == "Google Code":
        try:
            url = urllib2.urlopen(req)
            xml = url.read()
            doc = BeautifulSoup(xml)
        except Exception, e:
            error = "Sorry, I could not get "+data['project']+" issue #"+data['number']
            if not request:
                return error
            messages.error(request, error)
            return False

        status = doc.find("issues:state").contents[0]
        data['status'] = (status == "new" or status == "open" or status == "accepted" or status == "started") and "open" or "closed"
        data['title'] = doc.find("entry").find("title").contents[0]
        data['content'] = doc.find("content").contents[0]
        data['service'] = service.name

    elif service.name == "Github":
        try:
            result = json.load(urllib2.urlopen(req))
        except Exception, e:
            error = "I had an issue getting "+data['user']+" / "+data['project']+" issue #"+data['number']
            if not request:
                return error
            messages.error(request, error)

        data['status'] = result['state']
        data['title'] = result['title']
        data['content'] = result['body']
        if "closed_by" in result:
            data['closed_by'] = result['closed_by']
        data['service'] = service.name
        data['avatar_url'] = result['user']['avatar_url']

    return data

def add_issue_to_database(request):


    issue = request.session.get('issue', False)
    service = Service.objects.get(name=issue['service'])

    try:
        db_issue = Issue.objects.get(service=service, number=issue['number'], project=issue['project'])
        if db_issue.status == "paid":
            error = "I see that issue has been closed and paid already."
            messages.error(request, error)
            return False
    except:

        db_issue = Issue(
        service=service,
        number=issue['number'],
        project=issue['project'],
        user=issue.has_key('user') and issue['user'] or '',
        title=issue['title'],
        content=issue['content'][:350],
        status = issue['status'])
        filename, file = get_image_for_issue(service, issue)
        if filename:
            db_issue.image.save(filename, file)
        db_issue.save()
        if not settings.DEBUG:
            create_comment(db_issue)

    ends = issue['limit']
    hour_day = ends[-1]
    number = ends.rstrip(hour_day)
    if hour_day == "h":
        limit = datetime.timedelta(hours=int(number))
    else:
        limit = datetime.timedelta(days=int(number))
    bounty = Bounty(user=request.user, issue=db_issue, price=issue['bounty'], ends=datetime.datetime.now()+limit )
    bounty.save()
    alert_watchers_increase(db_issue, int(request.GET.get('bounty', 0)))
    del request.session['issue']
    return True

def alert_watchers_increase(issue, bounty):
    watchers = Watcher.objects.filter(issue=issue.id, bounty=True)
    sender = "Coder Bounty<%s>" % settings.SERVER_EMAIL
    subject = "%s issue #%s bounty is now $%s" % (issue.project, issue.number, issue.bounty())
    text = """$%s was added.
                <p>Description: %s.</p>
                Go to http://coderbounty.com/#%s to see more.
            """ % (issue.bounty(), issue.content, issue.id)
    for watcher in watchers:
        message = EmailMultiAlternatives(
            subject,
            from_email=sender,
            to=[watcher.user.email]
        )

        message.attach_alternative(
            text,
            "text/html"
        )
        message.send()


def get_image_for_issue(service, issue):

    if service.name == "Google Code":
        image_path = "/p/"+issue['project']+"/logo"

        img_temp = NamedTemporaryFile()
        try:
            url_opened=urllib2.urlopen("http://"+service.domain+image_path)
        except Exception, e:
            return False, False
        if url_opened:
            buffer = url_opened.read()
            if len(buffer) > 0:
                img_temp.write(buffer)
                img_temp.flush()
                return issue['project']+".jpg", File(img_temp)

        img_temp.flush()

    if service.name == "Github":
        org_url = service.api_url + "/orgs/" + issue['project']
        req = urllib2.Request(org_url, None, {'Content-Type': 'application/json'})
        try:
            result = json.load(urllib2.urlopen(req))
        except Exception, e:
            return False, False
        img_temp = NamedTemporaryFile()
        try:
            url_opened=urllib2.urlopen(result['avatar_url'])
            file_ext = url_opened.info()['Content-Type'].split("/")[1]
        except Exception, e:
            return False, False
        if url_opened:
            buffer = url_opened.read()
            if len(buffer) > 0:
                img_temp.write(buffer)
                img_temp.flush()
                return issue['project']+"."+file_ext, File(img_temp)

    if service.name == "Bitbucket":
        org_url = service.api_url + "/repositories/" + issue['user'] + "/" + issue['project']
        req = urllib2.Request(org_url, None, {'Content-Type': 'application/json'})
        result = json.load(urllib2.urlopen(req))
        logo = result['logo']
        img_temp = NamedTemporaryFile()
        try:
            url_opened=urllib2.urlopen(logo)
        except Exception, e:
            return False, False
        if url_opened:
            buffer = url_opened.read()
            if len(buffer) > 0:
                img_temp.write(buffer)
                img_temp.flush()
                return issue['project']+".png", File(img_temp)

    return False, False


def get_twitter_count():
    twitter_count_url="http://urls.api.twitter.com/1/urls/count.json?url=http://coderbounty.com"
    req = urllib2.Request(twitter_count_url, None, {'Content-Type': 'application/json'})
    result = json.load(urllib2.urlopen(req))
    return result['count']

def get_facebook_count():
    facebook_count_url="https://graph.facebook.com/235042326555141"
    req = urllib2.Request(facebook_count_url, None, {'Content-Type': 'application/json'})
    result = json.load(urllib2.urlopen(req))
    return result['likes']


def create_comment(issue=None, comment=None):
    if not comment:
        comment = "A bounty has been placed on this issue, check it out at Coder Bounty! http://coderbounty.com/#"+str(issue.id)
    #see if we've commented already and just update
    #try to have one comment that we update
    return globals()["post_"+issue.service.name.replace(" ", "_").lower()+"_comment"](issue, comment)


def post_google_code_comment(issue, comment=""):

    auth_url = 'https://www.google.com/accounts/ClientLogin'
    auth_req_data = urllib.urlencode({'Email': settings.GOOGLE_CODE_USERNAME,
                                  'Passwd': settings.GOOGLE_CODE_PASSWORD,
                                  'service': 'code'})
    auth_req = urllib2.Request(auth_url, data=auth_req_data)
    auth_resp = urllib2.urlopen(auth_req)
    auth_resp_content = auth_resp.read()
    auth_resp_dict = dict(x.split('=') for x in auth_resp_content.split('\n') if x)
    auth_token = auth_resp_dict["Auth"]


    xml_data="""<?xml version='1.0' encoding='UTF-8'?>
    <entry xmlns='http://www.w3.org/2005/Atom' xmlns:issues='http://schemas.google.com/projecthosting/issues/2009'>
        <content type='html'>{comment}</content>
        <author>
            <name>coderbounty</name>
        </author>
        <issues:cc>
        <issues:uri>u/114883342009011078618/</issues:uri>
        <issues:username>coderbou...@gmail.com</issues:username>
        </issues:cc>
    </entry>""".format(comment=comment)
    base_url = issue.api_url().split("full")[0]+str(issue.number)+"/comments/full"
    code_req = urllib2.Request(base_url, xml_data)
    code_req.add_header('Content-Type', 'application/atom+xml')
    code_req.add_header('Authorization', 'GoogleLogin auth=%s' % auth_token)
    urllib2.urlopen(code_req)

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    url = urllib2.urlopen('https://accounts.google.com/ServiceLogin?service=code')
    html = url.read()
    doc = BeautifulSoup(html)
    galx_input = doc.find(attrs = dict(name = 'GALX'))
    galx = galx_input['value']

    params = urllib.urlencode({
    'Email' : settings.GOOGLE_CODE_USERNAME,
    'Passwd' : settings.GOOGLE_CODE_PASSWORD,
    'GALX' : galx})

    req = urllib2.Request('https://accounts.google.com/ServiceLoginAuth?service=code', params)
    req.add_header( 'Referer', "https://accounts.google.com/ServiceLogin?service=code" )
    url = urllib2.urlopen(req)

    url = urllib2.urlopen(issue.html_url())
    html = url.read()
    doc = BeautifulSoup(html)
    csrf_input = doc.find(attrs = dict(name = 'token'))
    codesite_token = csrf_input['value']

    url = urllib2.urlopen('http://code.google.com/p/'+issue.project+'/issues/setstar.do?alt=js&issueid='+str(issue.number)+'&starred=1&token='+codesite_token)
    return True


def post_bitbucket_comment(issue, comment=""):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    url = urllib2.urlopen('https://bitbucket.org/account/signin/')
    html = url.read()
    doc = BeautifulSoup(html)
    csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
    csrf_token = csrf_input['value']

    params = urllib.urlencode(dict(username = settings.BITBUCKET_USERNAME, password=settings.BITBUCKET_PASSWORD, csrfmiddlewaretoken = csrf_token, next = '/', submit = "Log in"))
    req = urllib2.Request('https://bitbucket.org/account/signin/', params)
    req.add_header( 'Referer', "https://bitbucket.org/account/signin/" )
    url = urllib2.urlopen(req)

    #we may not need this whole block
    #looked again on 1/2 - definitly looks like we can delete this block, please test
    url = urllib2.urlopen(issue.html_url)
    #maybe not needed html
    html = url.read()
    csrf_input = doc.find(attrs = dict(name = 'csrfmiddlewaretoken'))
    csrf_token = csrf_input['value']

    params = urllib.urlencode(dict(content=comment, csrfmiddlewaretoken=csrf_token))
    req = urllib2.Request(issue.html_url, params)
    req.add_header( 'Referer', issue.html_url )
    url = urllib2.urlopen(req)
    try:
        url = urllib2.urlopen(issue.html_url+'follow')
    except:
        pass
    return True



def post_github_comment(issue, comment=""):
    json_data= "{\"body\": \""+comment+"\"}"
    gh_url = issue.api_url()+'/comments'

    req = urllib2.Request(gh_url, data=json_data)
    base64string = base64.encodestring(
                '%s:%s' % (settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD))[:-1]
    authheader =  "Basic %s" % base64string
    req.add_header("Authorization", authheader)
    urllib2.urlopen(req)
    return True

def issue_counts():
    counts ={
        'open':Issue.objects.filter(status=Issue.OPEN_STATUS).annotate(Count('id')),
        'in_review':Issue.objects.filter(status=Issue.IN_REVIEW_STATUS).annotate(Count('id')),
        'paid':Issue.objects.filter(status=Issue.PAID_STATUS).annotate(Count('id')),
    }
    return counts

def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")

def post_to_slack(bounty):

    payload= {"text": str(bounty.user)+" placed a Bounty of $"+ str(bounty.price)+ " More details at http://coderbounty.com"+str(bounty.issue.get_absolute_url())}

    url = 'https://hooks.slack.com/services/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'
    r = requests.post(url, data=json.dumps(payload))