from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from website.views import UserProfileDetailView, \
    IssueDetailView, UserProfileEditView, LeaderboardView
from django.views.generic.base import TemplateView
from rest_framework import routers, serializers, viewsets
from website.models import Issue, Service
from django.contrib.auth.models import User
from website import views
<<<<<<< HEAD
=======
from django.conf import settings
from django.conf.urls.static import static
>>>>>>> 6fc10f727e20e95859652ab0a9d577142dd9f516

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'website.views.home', name='home'),
<<<<<<< HEAD
    url(r'^about/$',  TemplateView.as_view(template_name='about.html'), name='about'),
=======
    url(r'^post/$', 'website.views.create_issue_and_bounty', name='post'),
    url(r'^list/$', 'website.views.list', name='list'),
    url(r"^issue/(?P<slug>\w+)/$", IssueDetailView.as_view(), name="issue"),
    url(r'^issueTaken/$', 'website.views.issueTaken', name="Taker"),
    url(r'^issueTaken/(?P<id>\w+)/$', views.issueTakenById, name="Taker"),
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
>>>>>>> 6fc10f727e20e95859652ab0a9d577142dd9f516
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^edit_profile/$', login_required(UserProfileEditView.as_view()), name="edit_profile"),
    url(r'^help/$', TemplateView.as_view(template_name='help.html'), name='help'),
    url(r'^issue/(?P<slug>\w+)/$', IssueDetailView.as_view(), name="issue"),
    url(r'^issueTaken/$', 'website.views.issueTaken', name="Taker"),
    url(r'^issueTaken/(?P<id>\w+)/$', views.issueTakenById, name="Taker"),
    url(r'^leaderboard/$', LeaderboardView.as_view(), name="leaderboard"),
    url(r'^list/$', 'website.views.list', name='list'),
    url(r'^parse_url_ajax/$', 'website.views.parse_url_ajax', name='parse_url_ajax'),
    url(r'^post/$', 'website.views.create_issue_and_bounty', name='post'),
    url(r'^profile/$', 'website.views.profile', name='profile'),
    url(r'^profile/(?P<slug>[^/]+)/$', UserProfileDetailView.as_view(), name="profile"),
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt')),
    url(r'^terms/$', TemplateView.as_view(template_name='terms.html'), name='terms'),
)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'date_joined', 'last_login')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('name', 'domain', 'template', 'regex', 'type', 'api_url', 'link_template')


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class IssueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Issue
        fields = ('id', 'service', 'project', 'user', 'number', 'image',
                  'title', 'content', 'language', 'status', 'winner', 'paid',
                  'closed_by', 'created', 'modified', 'notified_user', 'views')


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'issues', IssueViewSet)
router.register(r'services', ServiceViewSet)

urlpatterns += (
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
