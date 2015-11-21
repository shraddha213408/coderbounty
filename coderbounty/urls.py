from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from website.views import UserProfileDetailView, IssueDetailView, UserProfileEditView, LeaderboardView
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

    url(r"^leaderboard/$", LeaderboardView.as_view(), name="leaderboard"),

    url(r'^help/$', 'website.views.help', name='help'),
    url(r'^terms/$', 'website.views.terms', name='terms'),   
    url(r'^about/$', 'website.views.about', name='about'),  
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt')),
)
