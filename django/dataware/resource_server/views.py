from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Template, RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from dwlib import request_get, url_keys, form_label
import dwlib
from libauth.models import Registration as CRR
from libauth.models import Registration
from libauth.models import regist_steps, regist_dealer, REGIST_STATUS, REGIST_TYPE
from libauth.models import find_key_by_value_regist_type, find_key_by_value_regist_status, find_key_by_value_regist_request_media

def hello(request):
    return HttpResponse('hello, resource')


regist_callback_me = 'http://localhost:8001/resource/regist'

class regist_dealer_resource(regist_dealer):
    def regist_init(self): pass
    def registrant_request(self): 
        pass
    def register_owner_redirect(self):
        register_redirect_action = request_get(self.request.REQUEST, url_keys.regist_redirect_action)
        if register_redirect_action == url_keys.regist_redirect_action_redirect:
            url = request_get(self.request.REQUEST, url_keys.regist_redirect_url)
            return HttpResponseRedirect(url)
        if register_redirect_action == url_keys.regist_redirect_action_login_redirect:
            url = request_get(self.request.REQUEST, url_keys.regist_redirect_url)
            return HttpResponseRedirect('/accounts/login?next=%s'%url)
        registrant_callback = request_get(self.request.REQUEST, url_keys.regist_callback)
        regist_type = request_get(self.request.REQUEST, url_keys.regist_type)
        registrant_request_token = request_get(self.request.REQUEST, url_keys.registrant_request_token)
        registrant_request_scope = request_get(self.request.REQUEST, url_keys.registrant_request_scope) # may check it is in scope or not
        registrant_request_reminder = request_get(self.request.REQUEST, url_keys.registrant_request_reminder)
        registrant_request_media = request_get(self.request.REQUEST, url_keys.registrant_request_media)
        registrant_request_user_public = request_get(self.request.REQUEST, url_keys.registrant_request_user_public)
        register_redirect_token = dwlib.token_create(registrant_callback)
        params = {
            url_keys.regist_status: REGIST_STATUS.register_owner_grant,
            url_keys.regist_type: REGIST_TYPE.catalog_resource,
            url_keys.register_redirect_token:register_redirect_token,
        }
        url_params = dwlib.urlencode(params)
        url = '%s?%s'%(regist_callback_me, url_params)
        regist_type_key = find_key_by_value_regist_type(regist_type)
        regist_status_key = find_key_by_value_regist_status(REGIST_STATUS.register_owner_redirect)
        registrant_request_media_key = find_key_by_value_regist_request_media(registrant_request_media)
        obj, created = Registration.objects.get_or_create(
            regist_type=regist_type_key, 
            regist_status=regist_status_key, 
            registrant_request_token=registrant_request_token, 
            registrant_request_scope=registrant_request_scope, 
            registrant_callback=registrant_callback, 
            register_callback=regist_callback_me, 
            registrant_request_reminder=registrant_request_reminder, 
            registrant_request_user_public=registrant_request_user_public,
            registrant_request_media=registrant_request_media_key,
            register_redirect_token=register_redirect_token)
        c = {
            "register_redirect_token":{
                'label': url_keys.register_redirect_token,
                'value': register_redirect_token,
                },
            "regist_redirect_url": {
                'label': url_keys.regist_redirect_url,
                'value': url,
                },
            'regist_status':{
                'label': url_keys.regist_status,
                'value': REGIST_STATUS.register_owner_redirect,
                },
            'register_redirect_action':{
                'label': url_keys.regist_redirect_action,
                'login_redirect': url_keys.regist_redirect_action_login_redirect,
                'redirect': url_keys.regist_redirect_action_redirect,
                },
            }
        context = RequestContext(self.request, c)
        return render_to_response("regist_owner_redirect.html", context)
        #return HttpResponseRedirect('http://localhost:8001/resource/regist?REGIST_STATUS=REGISTER_OWNER_REDIRECT')
    def register_owner_grant(self): 
        # requrie user to login first if not, otherwise, will display the previous page, use another params to see
        return HttpResponse("hello grant")
    def register_grant(self): pass
    def registrant_owner_redirect(self): pass
    def registrant_owner_grant(self): pass
    def registrant_confirm(self): pass
    def register_activate(self): pass
    def regist_finish(self): pass
    
def regist(request):
    # if no correct status is matched
    return regist_steps(regist_dealer_resource(request), request)


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
    
