from django.conf.urls import patterns, include, url
from django.contrib import admin
#from django.views.generic.simple import direct_to_template

from django.contrib.auth import views as auth_views
admin.autodiscover()

handler404 = 'website.views.error_404_view'
handler500 = 'website.views.error_500_view'


urlpatterns = patterns('',
    ('^accounts/', include('allauth.urls')),
    ('^activity/', include('actstream.urls')),
    
    url(r'^$', 'website.views.home', name='home'),
    url(r'^post/$', 'website.views.post', name='post'),
    url(r'^list/$', 'website.views.list', name='list'),
    url(r'^issue/$', 'website.views.issue', name='issue'),
    url(r'^profile/$', 'website.views.profile', name='profile'),
    url(r'^parse_url_ajax/$', 'website.views.parse_url_ajax', name='parse_url_ajax'),



    url(r'^add/$', 'website.views.add', name='add'),
    url(r'^watch/$', 'website.views.watch', name='watch'),
    url(r'^login/$', 'website.views.login_async', name='login'),
    url(r'^join/$', 'website.views.join', name='join'),
    url(r'^logout/$', 'website.views.logout_view', name='logout'),
    
    url(r'^load_issue/$', 'website.views.load_issue', name='load_issue'),
    #url(r'^issue/(?P<id>\d)/$', 'website.views.issue', name='issue'),
    url(r'^wepay_auth/$', 'website.views.wepay_auth', name='wepay_auth'),
    url(r'^wepay_callback$', 'website.views.wepay_callback', name='wepay_callback'),
    url(r'^post_comment$', 'website.views.post_comment', name='post_comment'),
    url(r'^verify/(?P<service_slug>[a-zA-Z0-9_.-]+)/$', 'website.views.verify', name='verify'),
    url(r'^help/$', 'website.views.help', name='help'),
    url(r'^terms/$', 'website.views.terms', name='terms'),   
    url(r'^about/$', 'website.views.about', name='about'),  
    
    url(r'^passreset/$', auth_views.password_reset, name='forgot_password1'),
    url(r'^passresetdone/$', auth_views.password_reset_done, name='forgot_password2'),
    url(r'^passresetconfirm/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$', auth_views.password_reset_confirm, name='forgot_password3'),
    url(r'^passresetcomplete/$', auth_views.password_reset_complete, name='forgot_password4'),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/images/favicon.ico'}),
    #url(r'^robots.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    
    #url(r'^social_auth/', include('social_auth.urls')),
    #url(r'^profiles/', include('profiles.urls')),


)

#from django.conf import settings
#from django.conf.urls.static import static
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
