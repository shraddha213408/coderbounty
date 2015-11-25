from .forms import IssueCreateForm, BountyCreateForm, UserProfileForm
from actstream import action
from actstream.models import Action
from actstream.models import user_stream
from BeautifulSoup import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.models import Site
from django.core import serializers
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum, Count
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponse
from django.shortcuts import render_to_response, RequestContext, redirect, get_object_or_404, render
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import UpdateView
from models import Issue, UserProfile, Bounty, Service, Taker
from utils import get_issue, add_issue_to_database, get_twitter_count, get_facebook_count, create_comment, issue_counts, leaderboard, get_hexdigest, post_to_slack, submit_issue_taker
from wepay import WePay
import cookielib
import time
from time import gmtime, strftime
import datetime
import json
import random
import re
import string
import urllib
import urllib2

def parse_url_ajax(request):
     url = request.POST.get('url', '')
     issue = get_issue(request, url)
     return HttpResponse(json.dumps(issue))

def home(request, template="index.html"):
    activities = Action.objects.all()[0:10]
    context = {
        'activities': activities,
        'leaderboard': leaderboard(),
    }
    response = render_to_response(template, context, context_instance=RequestContext(request))
    return response

@login_required
def create_issue_and_bounty(request):
    languages = []
    for lang in Issue.LANGUAGES:
        languages.append(lang[0])
    user = request.user

    if request.method == 'GET':
        if request.GET.get('url'):
            issue_data = get_issue(request, request.GET.get('url'))
            if not issue_data:
                messages.error(request, 'Please provide an valid issue url')
                return redirect('/post')

            form = IssueCreateForm(
                initial={
                'issueUrl': request.GET.get('url'), 
                'title': issue_data['title'],
                'content': issue_data['content'] or "Added from Github" 
                })
        else:
             form = IssueCreateForm()
        return render(request, 'post.html', {
            'languages': languages,
            'form': form,
        })
    if request.method == 'POST':
        url = request.POST.get('issueUrl','')
        if not url:
            messages.error(request, 'Please provide an issue url')
            return render(request, 'post.html', {
                'languages': languages
            })
        issue_data = get_issue(request, url)
        if issue_data:
            service = Service.objects.get(name=issue_data['service'])
            instance = Issue(number = issue_data['number'],
            project=issue_data['project'],user = issue_data['user'],service=service)
        else:
            return render(request, 'post.html', {
                'languages': languages,
                'message':'Please provide a propper issue url',
            })
        form = IssueCreateForm(request.POST, instance=instance)
        bounty_form = BountyCreateForm(request.POST)
        bounty_form_is_valid = bounty_form.is_valid()
        if form.is_valid() and bounty_form_is_valid:
            price = bounty_form.cleaned_data['price']
            if int(price) < 5:
                return render(request, 'post.html', {
                	'languages': languages,
                	'message':'Bounty must be greater than $5',
                })
            try:
                issue = form.save()
            except:
                issue = Issue.objects.get(number = issue_data['number'], 
                    project=issue_data['project'],user = issue_data['user'],service=service)
                #issue exists
            

            bounty_instance = Bounty(user = user,issue = issue,price = price)
            
            data = serializers.serialize('xml', [ bounty_instance, ])
            
            wepay = WePay(settings.WEPAY_IN_PRODUCTION, settings.WEPAY_ACCESS_TOKEN)
            wepay_data = wepay.call('/checkout/create', {
                'account_id': settings.WEPAY_ACCOUNT_ID,
                'amount': request.POST.get('grand_total'),
                'short_description': 'CoderBounty',
                'long_description': data,
                'type': 'service',
                'redirect_uri': request.build_absolute_uri(issue.get_absolute_url()),
                'currency': 'USD'
            })
            if "error_code" in wepay_data:
                messages.error(request, wepay_data['error_description'])
                return render(request, 'post.html', {
                    'languages': languages
                })

            return redirect(wepay_data['checkout_uri'])

        else:
            return render(request, 'post.html', {
                'languages': languages,
                'message':form.errors,
                'errors': form.errors,
                'form':form,
                'bounty_errors':bounty_form.errors,
            })


def list(request):
    # q=''
    # status=''
    # order='-bounty'
    # if q:
    #     entry_query = get_query(q.strip(), ['title', 'content', 'project', 'number', ])
    #     issues = Issue.objects.filter(entry_query)
    # else:
    
    issues = Issue.objects.all().order_by('-created')

    # if status and status != "all":
    #     issues = issues.filter(status=status)

    # if status == "open" or status == '' or status == None:
    #     issues = issues.filter(bounty__ends__gt=datetime.datetime.now())

    # if order.find('bounty') > -1:
    #     issues = issues.annotate(bounty_sum=Sum('bounty__price')).order_by(order + '_sum')

    # if order.find('watchers') > -1:
    #     issues = issues.annotate(watchers_count=Count('watcher')).order_by(order + '_count')

    # if order.find('project') > -1:
    #     issues = issues.annotate(Count('id')).order_by(order)

    # if order.find('number') > -1:
    #     issues = issues.annotate(Count('id')).order_by(order)

    context = {
         'issues': issues,
    }
    response = render_to_response('list.html', context, context_instance=RequestContext(request))
    return response


# #@ajax_login_required
# def add(request):

#     if issue and issue['status'] == "open":
#         issue['bounty'] = int(request.GET.get('bounty', 0))
#         issue['limit'] = request.GET.get('limit', 0)
#         request.session['issue'] = issue
#         if request.user.get_profile().balance and (int(request.user.get_profile().balance) > int(request.GET.get('bounty', 0))):
#             if add_issue_to_database(request):
#                 user_profile = UserProfile.objects.get(user=request.user)
#                 user_profile.balance = int(user_profile.balance) - int(request.GET.get('bounty', 0))
#                 request.user.get_profile().balance = user_profile.balance
#                 user_profile.save()
#                 message = "<span style='color: #8DC63F; font-weight:bold;'>$"\
#                     + request.GET.get('bounty', 0) + " <span style='color:#4B4B4B'>bounty added to issue </span><strong>#"\
#                     + str(issue['number']) + "</strong>"
#                 messages.add_message(request, messages.SUCCESS, message)

#         else:
#             try:
#                 wepay = WePay(production=settings.IN_PRODUCTION, access_token=settings.WEPAY_ACCESS_TOKEN)

#                 ctx = {
#                 'account_id': settings.ACCOUNT_ID,
#                 'short_description': '$' + request.GET.get('bounty', 0) + " bounty on " + issue['project'] + " issue #" + str(issue['number']),
#                 'type': 'PERSONAL',
#                 'amount': int(request.GET.get('bounty', 0)),
#                 'mode': 'iframe'
#                 }
#                 wepay_call_return = wepay.call('/checkout/create', ctx)
#                 checkout_uri = wepay_call_return['checkout_uri']
#                 message = "Adding bounty to issue #" + str(issue['number'])
#                 messages.add_message(request, messages.SUCCESS, message)
#             except Exception, e:
#                 message = "%s" % e

#     else:
#         if issue['status'] != "open":
#             error = "Issue must be open, it is " + issue['status']
#             messages.error(request, error)
#         storage = messages.get_messages(request)
#         for item in storage:
#             message += str(item)

#     context = {
#         'message': message,
#         'url': url,
#         'issue': issue,
#         'wepay_host': settings.DEBUG and "stage" or "www",
#         'checkout_uri': checkout_uri,
#         'balance': str(request.user.get_profile().balance),
#     }

#     if request.is_ajax():
#         storage = messages.get_messages(request)
#         for item in storage:
#             message += str(item)
#         return HttpResponse(json.dumps(context))

#     q = request.GET.get('q', '')
#     status = request.GET.get('status', 'open')
#     order = request.GET.get('order', '-bounty')
#     context['issues'] = get_issues(q, status, order)

#     template = "index.html"

#     return render_to_response(template, context, context_instance=RequestContext(request))


# def wepay_auth(request):
#     wepay = WePay(settings.IN_PRODUCTION)
#     return redirect(wepay.get_authorization_url("http://" + Site.objects.get(id=settings.SITE_ID).domain + '/wepay_callback', settings.CLIENT_ID))


# def wepay_callback(request):
#     code = request.GET.get('code')
#     wepay = WePay(settings.IN_PRODUCTION)
#     response = wepay.get_token("http://" + Site.objects.get(id=settings.SITE_ID).domain + '/wepay_callback', settings.CLIENT_ID, settings.CLIENT_SECRET, code)
#     messages.add_message(request, messages.SUCCESS, "Wepay token created !" + response['access_token'])
#     return redirect("/")


# def post_comment(request):
#     issue = Issue.objects.get(number='34')
#     create_comment(issue, "Is this still active????")
#     return HttpResponse("True")


# def normalize_query(query_string,
#                     findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
#                     normspace=re.compile(r'\s{2,}').sub):
#     return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]






def profile(request):
    """Redirects to profile page if the requested user is loggedin
    """ 
    try:
        return redirect('/profile/'+request.user.username)
    except Exception:
        return redirect('/')


class UserProfileDetailView(DetailView):
    model = get_user_model()
    slug_field = "username"
    template_name = "profile.html"

    def get_object(self, queryset=None):
        user = super(UserProfileDetailView, self).get_object(queryset)
        UserProfile.objects.get_or_create(user=user)
        return user

    def get_context_data(self, **kwargs):
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)
        context['activities'] = user_stream(self.get_object(), with_user_activity=True)        
        return context


class UserProfileEditView(SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "profiles/edit.html"
    success_message = 'Profile saved'

    def get_object(self, queryset=None):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

    def get_success_url(self):
        # return reverse("profile", kwargs={'slug': self.request.user})
        return reverse("edit_profile")

    def form_valid(self, form):
        user_id = form.cleaned_data.get("user")
        user = User.objects.get(id=user_id)
        user.first_name = form.cleaned_data.get("first_name")
        user.last_name = form.cleaned_data.get("last_name")
        user.email = form.cleaned_data.get("email")
        user.save()
        
        return super(UserProfileEditView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message 


class LeaderboardView(ListView):
    template_name="leaderboard.html"
    
    def get_queryset(self):
        return User.objects.all().annotate(null_position=Count('userprofile__balance')).order_by('-null_position', '-userprofile__balance', '-last_login')
    
    def get_context_data(self, **kwargs):
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        context['leaderboard'] = leaderboard()        
        return context

def help(request):
    return render_to_response("help.html", context_instance=RequestContext(request))

def terms(request):
    return render_to_response("terms.html", context_instance=RequestContext(request))

def about(request):
    return render_to_response("about.html", context_instance=RequestContext(request))

class IssueDetailView(DetailView):
    model = Issue
    slug_field = "id"
    template_name = "issue.html"

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('checkout_id'):
            wepay = WePay(settings.WEPAY_IN_PRODUCTION, settings.WEPAY_ACCESS_TOKEN)
            wepay_data = wepay.call('/checkout/', {
                'checkout_id': self.request.GET.get('checkout_id'),
            })
            
            for obj in serializers.deserialize("xml", wepay_data['long_description'], ignorenonexistent=True):
                obj.object.created = datetime.datetime.now()
                obj.object.checkout_id = self.request.GET.get('checkout_id')
                obj.save()
                action.send(self.request.user, verb='placed a $' + str(obj.object.price) + ' bounty on ', target=obj.object.issue)
            	post_to_slack(obj.object)

        
        return super(IssueDetailView, self).get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(IssueDetailView, self).get_context_data(**kwargs)
        context['leaderboard'] = leaderboard()        
        return context

    def get_object(self):
            object = super(IssueDetailView, self).get_object()
            object.views = object.views + 1
            object.save()
            return object
def issueTaken(request):
    if request.method == 'POST':
        issueId =  request.POST.get('id')
        _date = strftime("%c")
        today = datetime.datetime.today()
        response_data = {}
        response_data['status'] = 'taken'
        response_data['issueTakenTime'] = _date

        # issue = Issue.objects.get(pk=issueId)
        issue_take_data = {
            "issue": issueId,
            "issueStartTime": today,
            "user": request.user,
            "status": "taken"
        }
        username = issue_take_data["user"]
        response_data['username'] = str(username)
        issueTaken = submit_issue_taker(issue_take_data)
        return HttpResponse(json.dumps(response_data), content_type="application/json")