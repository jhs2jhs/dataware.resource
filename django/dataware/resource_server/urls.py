from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^hello', 'resource_server.views.hello'),

    # registration with catalog
    # REQUEST
    url(r'^catalog_register', 'resource_server.views.catalog_register'),

)
