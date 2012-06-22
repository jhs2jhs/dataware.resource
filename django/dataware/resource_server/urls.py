from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^hello', 'resource_server.views.hello'),

    url(r'^regist', 'resource_server.views.regist'),


)
