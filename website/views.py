from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponse
from django.core.mail import send_mail
#from django.views.decorators.cache import cache_page
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from models import Issue, Watcher, UserProfile, Service, UserService
from utils import get_issue, add_issue_to_database, get_twitter_count, get_facebook_count, create_comment, issue_counts, leaderboard, get_hexdigest
#from decorators import ajax_login_required

from django.shortcuts import get_object_or_404, render

#from django.utils 
import json
from django.contrib import messages
from django.db.models import Q
import re
import datetime
from django.db.models import Sum, Count
#from wepay import WePay
from django.contrib.sites.models import Site
import urllib
import urllib2
import cookielib

from BeautifulSoup import BeautifulSoup
import string
import random


#TODO:
#setup new framework on heroku (in progress now)

#https://assembly.com/coder-bounty
#these tasks currently have bounties on them

#implement adding an issue
# - get issue image
# - add issue to databas
#integrate activity stream
#implement ajax loader for posting a bounty /post (done)
#implement leader board
#auto count for total bounties won
#make circles on homepage links
#integrate avatars
#create browser extension to post bounties from github / bitbucket


#from forms import UserCreationForm

#@cache_page(60 * 15)

def parse_url_ajax(request):
    url = request.POST.get('url', '')
    issue = get_issue(request, url)
    return HttpResponse(json.dumps(issue))


def home(request,
    template="index.html",
    page_template="issues.html"):

    ## print request.session.get('coin_count')
    ## print request.session.get('coin_dates')

    ## day_of_year = datetime.datetime.strftime(datetime.datetime.now(), "%j")
    ## if "coin_dates" in request.session:
        ## coin_dates = request.session.get('coin_dates')
        ## if not day_of_year in coin_dates:
            ## coin_count =  request.session.get('coin_count')
            ## request.session['coin_count']=coin_count+1
            ## request.session['coin_dates'].append(day_of_year)
    ## else:
        ## request.session['coin_count']=1
        ## request.session['coin_dates']=[day_of_year,]

    # if request.GET.get('checkout_id') and request.session.get('issue'):

    #     wepay = WePay(production=settings.IN_PRODUCTION, access_token=settings.WEPAY_ACCESS_TOKEN)
    #     ctx = {
    #         'checkout_id': request.GET.get('checkout_id'),
    #         }
    #     wepay_call_return = wepay.call('/checkout', ctx)
    #     if wepay_call_return['state'] == "authorized":
    #         request.session['issue']['bounty'] = wepay_call_return['amount']
    #         message = "$" + str(request.session['issue']['bounty']) + " bounty added to " +\
    #         request.session['issue']['project'] + " issue #" + str(request.session['issue']['number'])
    #         if add_issue_to_database(request):
    #             messages.add_message(request, messages.SUCCESS, message)

    status = request.GET.get('status', 'open')
    order = request.GET.get('order', '-bounty')
    q = request.GET.get('q', '')

    issues = get_issues(q, status, order)

    if request.is_ajax():
        template = page_template

    context = {
        'issues': issues,
        'issue_counts': issue_counts(),
        'page_template': page_template,
        'q': q,
        'leaderboard': leaderboard(),
        'wepay_host': settings.DEBUG and "stage" or "www",
        'status': status,
        #'form': UserCreationForm()
    }

    day_of_year = datetime.datetime.strftime(datetime.datetime.now(), "%j")
    ## day_of_year = str(int(day_of_year) + 2)
    # if request.user.is_authenticated():
    #     if Coin.objects.add_coin_for_user(request.user, request):
    #         context.update({'coin_added': 1})
    #     response = render_to_response(template, context, context_instance=RequestContext(request))
    # else:
    #     try:
    #         coins_count = int(request.COOKIES.get('coins', 0))
    #     except ValueError:
    #         coins_count = 0
    #     if day_of_year != request.COOKIES.get('day'):
    #         coins_count += 1
    #         context.update({'coin_added': 1})
    #         response = render_to_response(template, context, context_instance=RequestContext(request))
    #         response.set_cookie('day', day_of_year, max_age=3600 * 24)
    #         response.set_cookie('coins', coins_count, max_age=3600 * 24 * 365 * 5)
    #     elif coins_count == 0:
    #         coins_count += 1
    #         context.update({'coin_added': 1})
    #         response = render_to_response(template, context, context_instance=RequestContext(request))
    #         response.set_cookie('coins', coins_count, max_age=3600 * 24 * 365 * 5)
    #     else:
    #         
    response = render_to_response(template, context, context_instance=RequestContext(request))
    return response

def post(request):
    return render(request, 'post.html')

def list(request):
    return render(request, 'list.html')

def issue(request):
    return render(request, 'issue.html')

#@ajax_login_required
def add(request):
    message = ''
    url = ''
    error = ''
    checkout_uri = ''

    if not request.GET.get('bounty', None):
        error = "Please enter a bounty"
    if not request.GET.get('limit', None):
        error = "Please enter a time limit"
    if not request.GET.get('url', None):
        error = "Please enter a Github, Google Code or Bitbucket issue"

    if error:
        if request.is_ajax():
            return HttpResponse(error)
        else:
            messages.error(request, error)
            return redirect('/')

    url = request.GET.get('url', None)
    issue = get_issue(request, url)

    if issue and issue['status'] == "open":
        issue['bounty'] = int(request.GET.get('bounty', 0))
        issue['limit'] = request.GET.get('limit', 0)
        request.session['issue'] = issue
        if request.user.get_profile().balance and (int(request.user.get_profile().balance) > int(request.GET.get('bounty', 0))):
            if add_issue_to_database(request):
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.balance = int(user_profile.balance) - int(request.GET.get('bounty', 0))
                request.user.get_profile().balance = user_profile.balance
                user_profile.save()
                message = "<span style='color: #8DC63F; font-weight:bold;'>$"\
                    + request.GET.get('bounty', 0) + " <span style='color:#4B4B4B'>bounty added to issue </span><strong>#"\
                    + str(issue['number']) + "</strong>"
                messages.add_message(request, messages.SUCCESS, message)

        else:
            try:
                wepay = WePay(production=settings.IN_PRODUCTION, access_token=settings.WEPAY_ACCESS_TOKEN)

                ctx = {
                'account_id': settings.ACCOUNT_ID,
                'short_description': '$' + request.GET.get('bounty', 0) + " bounty on " + issue['project'] + " issue #" + str(issue['number']),
                'type': 'PERSONAL',
                'amount': int(request.GET.get('bounty', 0)),
                'mode': 'iframe'
                }
                wepay_call_return = wepay.call('/checkout/create', ctx)
                checkout_uri = wepay_call_return['checkout_uri']
                message = "Adding bounty to issue #" + str(issue['number'])
                messages.add_message(request, messages.SUCCESS, message)
            except Exception, e:
                message = "%s" % e

    else:
        if issue['status'] != "open":
            error = "Issue must be open, it is " + issue['status']
            messages.error(request, error)
        storage = messages.get_messages(request)
        for item in storage:
            message += str(item)

    context = {
        'message': message,
        'url': url,
        'issue': issue,
        'wepay_host': settings.DEBUG and "stage" or "www",
        'checkout_uri': checkout_uri,
        'balance': str(request.user.get_profile().balance),
    }

    if request.is_ajax():
        storage = messages.get_messages(request)
        for item in storage:
            message += str(item)
        return HttpResponse(json.dumps(context))

    q = request.GET.get('q', '')
    status = request.GET.get('status', 'open')
    order = request.GET.get('order', '-bounty')
    context['issues'] = get_issues(q, status, order)

    template = "index.html"

    return render_to_response(template, context, context_instance=RequestContext(request))


def wepay_auth(request):
    wepay = WePay(settings.IN_PRODUCTION)
    return redirect(wepay.get_authorization_url("http://" + Site.objects.get(id=settings.SITE_ID).domain + '/wepay_callback', settings.CLIENT_ID))


def wepay_callback(request):
    code = request.GET.get('code')
    wepay = WePay(settings.IN_PRODUCTION)
    response = wepay.get_token("http://" + Site.objects.get(id=settings.SITE_ID).domain + '/wepay_callback', settings.CLIENT_ID, settings.CLIENT_SECRET, code)
    messages.add_message(request, messages.SUCCESS, "Wepay token created !" + response['access_token'])
    return redirect("/")


def post_comment(request):
    issue = Issue.objects.get(number='34')
    create_comment(issue, "Is this still active????")
    return HttpResponse("True")


#@ajax_login_required
def watch(request):
    if request.GET.get('issue', None):

        issue_id = request.GET.get('issue', None)
        bounty = request.GET.get('bounty', False)
        status = request.GET.get('status', False)
        issue = get_object_or_404(Issue, pk=issue_id)

        watcher, created = Watcher.objects.get_or_create(user=request.user, issue=issue)
        watcher.bounty = bounty
        watcher.status = status
        watcher.save()
        if not bounty and not status:
            watcher.delete()

        return HttpResponse(issue.watchers().count())
    else:
        return HttpResponse("False")


def logout_view(request):
    logout(request)
    if request.is_ajax():
        return render_to_response("login_bar.html", {}, context_instance=RequestContext(request))
    return redirect('/')


def error_404_view(request):
    return HttpResponseNotFound('Not Found')


def error_500_view(request):
    return HttpResponseServerError('Internal server error')


def login_async(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    if username and password:
        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    context = {}
                    #if Coin.objects.add_coin_for_user(user, request):
                    #    context.update({'coin_added': 1})
                    return render_to_response("login_bar.html", context, context_instance=RequestContext(request))
                else:
                    return HttpResponse()
        except Exception:
            return HttpResponse()
    return HttpResponse()


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    query = None
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def get_issues(q='', status='', order='-bounty'):
    if q:
        entry_query = get_query(q.strip(), ['title', 'content', 'project', 'number', ])
        issues = Issue.objects.filter(entry_query)
    else:
        issues = Issue.objects.all()

    if status and status != "all":
        issues = issues.filter(status=status)

    if status == "open" or status == '' or status == None:
        issues = issues.filter(bounty__ends__gt=datetime.datetime.now())

    if order.find('bounty') > -1:
        issues = issues.annotate(bounty_sum=Sum('bounty__price')).order_by(order + '_sum')

    if order.find('watchers') > -1:
        issues = issues.annotate(watchers_count=Count('watcher')).order_by(order + '_count')

    if order.find('project') > -1:
        issues = issues.annotate(Count('id')).order_by(order)

    if order.find('number') > -1:
        issues = issues.annotate(Count('id')).order_by(order)

    return issues


def join(request):
    if request.method == 'POST':
        if not request.POST.get('agree'):
            return HttpResponse()
        if request.is_ajax():
            #form = UserCreationForm(request.POST)

            if form.is_valid():
                form.save()
                user = authenticate(username=request.POST.get('username'), password=request.POST.get('password1'))
                if user is not None:
                    if user.is_active:
                        user_profile = UserProfile(user=user)
                        user_profile.save()
                        login(request, user)
                        subject = "Welcome to Coder Bounty!"
                        body = "Thank you for joining Coder Bounty! Enjoy the site. http://coderbounty.com"
                        send_mail(subject, body, "Coder Bounty<" + settings.SERVER_EMAIL + ">", [request.POST.get('email')])
                        return render_to_response("login_bar.html", {}, context_instance=RequestContext(request))
                    else:
                        return HttpResponse()

    return HttpResponse()


def verify(request, service_slug):
    username = request.GET.get('username', False)
    verification_code = request.GET.get('verification_code', False)
    if username:
        service_name = ''.join(map(lambda s: s.capitalize() + " ", service_slug.split('-')))
        service = Service.objects.get(name=service_name)

        if verification_code:
            if request.session['random_string'] == verification_code:
                user_service = UserService(user=request.user, service=service, username=username)
                user_service.save()
                return HttpResponse("Thanks for verifying your account. Happy coding!")
            else:
                return HttpResponse("Please enter a valid verification code.")

        random_string = id_generator()
        request.session['random_string'] = random_string

        if service.name == "Bitbucket":
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)

            url = urllib2.urlopen('https://bitbucket.org/account/signin/')
            html = url.read()
            doc = BeautifulSoup(html)
            csrf_input = doc.find(attrs=dict(name='csrfmiddlewaretoken'))
            csrf_token = csrf_input['value']

            params = urllib.urlencode(dict(username=settings.BITBUCKET_USERNAME,
                password=settings.BITBUCKET_PASSWORD, csrfmiddlewaretoken=csrf_token, next='/', submit="Log in"))
            req = urllib2.Request('https://bitbucket.org/account/signin/', params)
            req.add_header('Referer', "https://bitbucket.org/account/signin/")
            url = urllib2.urlopen(req)

            url = urllib2.urlopen('https://bitbucket.org/account/notifications/send/?receiver=' + username)
            html = url.read()
            csrf_input = doc.find(attrs=dict(name='csrfmiddlewaretoken'))
            csrf_token = csrf_input['value']

            params = urllib.urlencode(dict(recipient=username, title="Coder Bounty " + service.name + " account verification code",
                message="Your validation code is " + random_string, csrfmiddlewaretoken=csrf_token))
            req = urllib2.Request('https://bitbucket.org/account/notifications/send/', params)
            req.add_header('Referer', 'https://bitbucket.org/account/notifications/send/?receiver=' + username)
            url = urllib2.urlopen(req)

            return HttpResponse("I sent a code to your " + service.name + " account.  Please enter it above and click verify again.")

        else:
            if service.name == "Github":
                url = urllib2.urlopen('https://github.com/' + username)
                html = url.read()
                doc = BeautifulSoup(html)
                msg_button = doc.find('a', "email")
                if msg_button:
                    encoded_email = msg_button['data-email']
                    decoded_email = urllib.unquote(encoded_email)
                else:
                    return HttpResponse("Please add your email address to your public github profile for verification, you can remove it afterwards.")

            elif service.name == "Google Code":
                decoded_email = username

            send_mail("Coder Bounty " + service.name + " account verification code", "Your validation code is " + random_string,
                "Coder Bounty<" + settings.SERVER_EMAIL + ">", [decoded_email])
            return HttpResponse("I sent a code to your " + service.name + " email address.  Please enter it above and click verify again.")
    return HttpResponse("Please enter a username")


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def profile(request):
    if request.POST:
        user = User.objects.get(id=request.user.id)

        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        if request.POST.get('payment_paypal', '') == "checked":
            user_profile.payment_service = "paypal"
        else:
            user_profile.payment_service = "wepay"
        user_profile.payment_service_email = request.POST.get('payment_service_email', '')
        save = False
        try:
            if user.username != request.POST.get('username', ''):
                user.username = request.POST.get('username', '')
                save = True
            if user.email != request.POST.get('email', ''):
                user.email = request.POST.get('email', '')
                save = True
            if request.POST.get('password', ''):
                algo = 'sha1'
                salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
                hsh = get_hexdigest(algo, salt, request.POST.get('password', ''))
                user.password = '%s$%s$%s' % (algo, salt, hsh)
                save = True
            if save:
                user.save()

        except Exception, e:
            return HttpResponse("{error}".format(error=e))

        user_profile.save()

        return HttpResponse("Your profile has been saved")

    return render_to_response("profile.html", context_instance=RequestContext(request))


def load_issue(request):
    if request.POST.get('issue[service]'):
        service = Service.objects.get(name=request.POST.get('issue[service]'))
        issue = Issue.objects.get(service=service, number=request.POST.get('issue[number]'), project=request.POST.get('issue[project]'))
        return render_to_response("single_issue.html", {'issue': issue}, context_instance=RequestContext(request))
    return HttpResponse()


#def issue(request, id):
#    issue = Issue.objects.get(id=id)
#    return render_to_response("issue.html", {'issue': issue}, context_instance=RequestContext(request))

def help(request):
    return render_to_response("help.html", context_instance=RequestContext(request))

def terms(request):
    return render_to_response("terms.html", context_instance=RequestContext(request))

def about(request):
    return render_to_response("about.html", context_instance=RequestContext(request))