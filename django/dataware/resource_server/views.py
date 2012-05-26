from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Template, RequestContext
from django.contrib.auth.models import User
from dwlib import request_get, url_keys, form_label
import dwlib
from libauth.models import CatalogResourceRegistration as CRR

def hello(request):
    return HttpResponse('hello, resource')

#####registeration with catalog#####
def catalog_register(request):
    params = request.REQUEST
    catalog_callback = request_get(params, url_keys.catalog_callback)
    catalog_request_token = request_get(params, url_keys.catalog_request_token)
    catalog_access_scope = request_get(params, url_keys.catalog_access_scope)
    #print params
    redirect_token = dwlib.token_create(catalog_callback)
    #print request_temp
    params = {
        url_keys.redirect_token:redirect_token
        }
    url_params = dwlib.urlencode(params)
    resource_callback = 'http://localhost:8001/resource/owner_request'
    url = '%s?%s'%(resource_callback, url_params)
    obj, created = CRR.objects.get_or_create(catalog_callback=catalog_callback, catalog_request_token=catalog_request_token, catalog_access_scope=catalog_access_scope, redirect_token=redirect_token, registration_status=2) # 2=redirect
    return HttpResponseRedirect(url)

@login_required
def owner_request(request):
    params = request.REQUEST
    #TODO to make user understand better, should provide catalog's description. 
    user_id = request.user.id
    redirect_token = request_get(params, url_keys.redirect_token)
    crr = CRR.objects.get(redirect_token=redirect_token)
    catalog_callback = crr.catalog_callback
    catalog_request_token = crr.catalog_request_token
    catalog_access_scope = crr.catalog_access_scope
    c = {
        'callback':{
            'label':form_label.owner_request_callback,
            'value':catalog_callback
            },
        'token':{
            'label':form_label.owner_request_token,
            'value':catalog_request_token
            },
        'scope':{
            'label':form_label.owner_request_scope,
            'value':catalog_access_scope
            },
        'action':{
            'allow':form_label.owner_request_action_allow,
            'decline':form_label.owner_request_action_decline
            },
        'user_id': user_id,
        'redirect_token':redirect_token,
        }
    context = RequestContext(request, c)
    return render_to_response('owner_request.html', context)

@login_required
def owner_grant(request):
    params = request.REQUEST
    #print params
    redirect_token = request_get(params, url_keys.redirect_token)
    user_id = request_get(params, url_keys.user_id)
    grant_action = request_get(params, url_keys.grant_action)
    if grant_action == form_label.owner_request_action_allow:
        return owner_auth(redirect_token, user_id)
    if grant_action == form_label.owner_request_action_decline:
        print 'decline'
        #TODO needs to solve later. 
        return HttpResponse('decline, need to be implemented')

def owner_auth(redirect_token, user_id):
    crr = CRR.objects.get(redirect_token=redirect_token)
    catalog_request_token = crr.catalog_request_token
    catalog_callback = crr.catalog_callback

    resource_callback = 'http://localhost:8001/resource/catalog_confirm' #TODO needs to be check with later access callback
    resource_request_token = dwlib.token_create(catalog_callback)
    resource_access_token = dwlib.token_create_user(catalog_callback, user_id)
    resource_validate_code = 'expire in 10 hours'
    user = User.objects.get(id=user_id)

    crr.user = user
    crr.registration_status = 3 # 3=grant
    crr.resource_callback = resource_callback
    crr.resource_request_token = resource_request_token
    resource_access_scope = crr.catalog_access_scope #TODO can both be same, as both are in different position.
    crr.resource_access_scope = resource_access_scope
    crr.resource_access_token = resource_access_token
    crr.resource_validate_code = resource_validate_code
    crr.save()

    params = {
        url_keys.catalog_request_token:catalog_request_token,
        url_keys.resource_access_token:resource_access_token,
        url_keys.resource_request_token:resource_request_token,
        url_keys.resource_validate_code:resource_validate_code,
        url_keys.resource_callback:resource_callback, 
        url_keys.resource_access_scope:resource_access_scope,
        }
    url_params = dwlib.urlencode(params)
    url = '%s?%s'%(catalog_callback, url_params)
    return HttpResponseRedirect(url)

def catalog_confirm(request):
    params = request.REQUEST
    catalog_access_token = request_get(params, url_keys.catalog_access_token)
    catalog_validate_code = request_get(params, url_keys.catalog_validate_code)
    resource_access_token = request_get(params, url_keys.resource_access_token)
    
    crr = CRR.objects.get(resource_access_token=resource_access_token)
    crr.catalog_access_token = catalog_access_token
    crr.catalog_validate_code = catalog_validate_code
    crr.registration_status = 5 # 5=confirm
    crr.save()

    return HttpResponse('registration finished')
    
