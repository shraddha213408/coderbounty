from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from website.views import UserProfileDetailView, IssueDetailView, UserProfileEditView
from django.views.generic.base import TemplateView

admin.autodiscover()


urlpatterns = patterns('',
    ('^accounts/', include('allauth.urls')),
    ('^activity/', include('actstream.urls')),
    
    url(r'^$', 'website.views.home', name='home'),
    url(r'^post/$', 'website.views.create_issue_and_bounty', name='post'),
    url(r'^list/$', 'website.views.list', name='list'),
    url(r"^issue/(?P<slug>\w+)/$", IssueDetailView.as_view(), name="issue"),
    url(r'^profile/$', 'website.views.profile', name='profile'),
    url(r"^profile/(?P<slug>[\w-]+)/$", UserProfileDetailView.as_view(), name="profile"),
    url(r'^edit_profile/$', login_required(UserProfileEditView.as_view()), name="edit_profile"),
    url(r'^parse_url_ajax/$', 'website.views.parse_url_ajax', name='parse_url_ajax'),

    #url(r'^add/$', 'website.views.add', name='add'),
    #url(r'^watch/$', 'website.views.watch', name='watch'),
    #url(r'^login/$', 'website.views.login_async', name='login'),
    ##url(r'^join/$', 'website.views.join', name='join'),
    #url(r'^logout/$', 'website.views.logout_view', name='logout'),
    
    #url(r'^load_issue/$', 'website.views.load_issue', name='load_issue'),
    #url(r'^wepay_auth/$', 'website.views.wepay_auth', name='wepay_auth'),
    #url(r'^wepay_callback$', 'website.views.wepay_callback', name='wepay_callback'),
    #url(r'^post_comment$', 'website.views.post_comment', name='post_comment'),
    #url(r'^verify/(?P<service_slug>[a-zA-Z0-9_.-]+)/$', 'website.views.verify', name='verify'),
    url(r'^help/$', 'website.views.help', name='help'),
    url(r'^terms/$', 'website.views.terms', name='terms'),   
    url(r'^about/$', 'website.views.about', name='about'),  
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt')),
)
