from django.conf.urls import *
#from books.views import hello
from books.views import *
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root':SITE_ROOT+'/templates/css'}),
    url(r'^script/(?P<path>.*)$', 'django.views.static.serve', {'document_root':SITE_ROOT+'/templates/scripts'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^time/(\d{1,2})/$', time),
    url(r'^books/$', books),
    url(r'^books/(?P<page>\d+)/$', books),
    url(r'^commit/$', commits),
    url(r'^commit/(?P<page>\d+)/$', commits),
    url(r'^diff/(?P<sha>.*)$', diff),

)
