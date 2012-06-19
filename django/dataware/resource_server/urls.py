from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^hello', 'resource_server.views.hello'),

    url(r'^regist', 'resource_server.views.regist'),

    # registration with catalog
    # REQUEST
    url(r'^catalog_register', 'resource_server.views.catalog_register'),
    # REDIRECT
    url(r'^owner_request$', 'resource_server.views.owner_request'),
    # GRANT
    url(r'^owner_grant$', 'resource_server.views.owner_grant'),
    # CONFIRM
    url(r'^catalog_confirm$', 'resource_server.views.catalog_confirm'),

)
