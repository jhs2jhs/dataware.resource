from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import Template, RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.core.exceptions import ObjectDoesNotExist
from dwlib import request_get, url_keys, form_label, error_response
import dwlib
from libauth.models import Registration
from libauth.models import REGIST_STATUS, REGIST_TYPE, TOKEN_TYPE
from libauth.models import find_key_by_value_regist_type, find_key_by_value_regist_status, find_key_by_value_regist_request_media
from libauth.views import regist_steps, regist_dealer
from libauth.views import method_regist_init, method_registrant_request

def hello(request):
    return HttpResponse('hello, resource')


regist_callback_me = 'http://localhost:8001/resource/regist'

def method_register_activate(request):
    print request.REQUEST
    register_access_token = request_get(request.REQUEST, url_keys.register_access_token)
    registrant_access_token = request_get(request.REQUEST, url_keys.registrant_access_token)
    registrant_access_validate = request_get(request.REQUEST, url_keys.registrant_access_validate)
    try:
        registration = Registration.objects.get(register_access_token=register_access_token)
    except ObjectDoesNotExist:
        return error_response(3, (url_keys.register_access_token, register_access_token))
    registration.registrant_access_token = registrant_access_token
    registration.registrant_access_validate = registrant_access_validate
    regist_status_key = find_key_by_value_regist_status(REGIST_STATUS.register_activate)
    registration.regist_status = regist_status_key
    registration.save()
    c = {
        'registrant_access_token':{
            'label': url_keys.registrant_access_token,
            'value': registrant_access_token,
            },
        'register_access_token':{
            'label': url_keys.registrant_access_token,
            'value': register_access_token,
            },
        'regist_activate_action':{
            'label': url_keys.regist_activate_action,
            'activate': url_keys.regist_activate_action_activate,
            },
        }
    context = RequestContext(request, c)
    return render_to_response("regist_activate.html", context)
    #return HttpResponse('hello')

class regist_dealer_resource(regist_dealer):
    def regist_init(self): pass
    def registrant_request(self): 
        pass
    def register_owner_redirect(self):
        return method_register_owner_redirect(self.request, regist_callback_me)
    def register_owner_grant(self): 
        # requrie user to login first if not, otherwise, will display the previous page, use another params to see
        regist_type = request_get(self.request.REQUEST, url_keys.regist_type)
        register_redirect_token = request_get(self.request.REQUEST, url_keys.register_redirect_token)
        user = self.request.user
        if not user.is_authenticated():
            params = {
                url_keys.regist_status: REGIST_STATUS.register_owner_grant,
                url_keys.regist_type: regist_type,
                url_keys.register_redirect_token:register_redirect_token,
                }
            url_params = dwlib.urlencode(params)
            url = '%s?%s'%(regist_callback_me, url_params)
            next_params = {
                "next":url
                }
            next_url_params = dwlib.urlencode(params)
            return HttpResponseRedirect('/accounts/login?%s'%next_url_params)
        registration = Registration.objects.get(register_redirect_token=register_redirect_token)
        regist_status_key = find_key_by_value_regist_status(REGIST_STATUS.register_owner_grant)
        registration.regist_status = regist_status_key
        registration.save()
        c = {
            "regist_callback":registration.registrant_callback,
            "regist_request_token":registration.registrant_request_token,
            "regist_request_scope":registration.registrant_request_scope,
            "regist_request_reminder":registration.registrant_request_reminder,
            "regist_redirect_action":{
                'label':url_keys.regist_redirect_action,
                'grant':url_keys.regist_redirect_action_grant,
                'modify_scope': url_keys.regist_redirect_action_modify_scope,
                'wrong_user': url_keys.regist_redirect_action_wrong_user,
                },
            'regist_status':{
                'label': url_keys.regist_status,
                'value': REGIST_STATUS.register_grant,
                },
            "register_redirect_token":{
                'label': url_keys.register_redirect_token,
                'value': register_redirect_token,
                },
            'regist_type':{
                'label': url_keys.regist_type,
                'value': REGIST_TYPE.catalog_resource,
                },
            }
        context = RequestContext(self.request, c)
        return render_to_response("regist_owner_grant.html", context)
    def register_grant(self): 
        print self.request.REQUEST
        user = self.request.user
        register_redirect_token = request_get(self.request.REQUEST, url_keys.register_redirect_token)
        regist_type = request_get(self.request.REQUEST, url_keys.regist_type)
        if not user.is_authenticated():
            params = {
                url_keys.regist_status: REGIST_STATUS.register_owner_grant,
                url_keys.regist_type: regist_type,
                url_keys.register_redirect_token:register_redirect_token,
                }
            url_params = dwlib.urlencode(params)
            url = '%s?%s'%(regist_callback_me, url_params)
            next_params = {
                "next":url
                }
            next_url_params = dwlib.urlencode(params)
            return HttpResponseRedirect('/accounts/login?%s'%next_url_params)
        # now, we have correct user here. We may need to check whether this token has been used before or not.
        print register_redirect_token
        try:
            if request_get(self.request.REQUEST, url_keys.register_request_action) == url_keys.register_request_action_request:
                print "hello"
                register_request_token = request_get(self.request.REQUEST, url_keys.register_request_token)
                registration = Registration.objects.get(register_request_token=register_request_token)
                if registration.user != user :
                    return error_response(2, ("user"))
                register_request_token = request_get(self.request.REQUEST, url_keys.register_request_token)
                if registration.register_request_token != register_request_token:
                    return error_response(2, (url_keys.register_request_token))
                register_request_scope = request_get(self.request.REQUEST, url_keys.register_request_scope)
                registration.register_request_scope = register_request_scope
                registration.save()
                params = {
                    url_keys.regist_status: REGIST_STATUS.registrant_owner_redirect,
                    url_keys.regist_type: regist_type,
                    url_keys.regist_callback: regist_callback_me,
                    url_keys.registrant_request_token: registration.registrant_request_token,
                    url_keys.register_access_token: registration.register_access_token,
                    url_keys.register_access_validate: registration.register_access_validate,
                    url_keys.register_request_token: registration.register_request_token,
                    url_keys.register_request_scope: registration.register_request_scope,
                    }
                url_params = dwlib.urlencode(params)
                url = '%s?%s'%(registration.registrant_callback, url_params)
                return HttpResponseRedirect(url)
            registration = Registration.objects.get(register_redirect_token=register_redirect_token)
            regist_status_key = find_key_by_value_regist_status(REGIST_STATUS.register_owner_grant)
            #if registration.regist_status != regist_status_key:
            #    return error_response(4, (url_keys.register_redirect_token, register_redirect_token))
        except ObjectDoesNotExist:
            return error_response(3, (url_keys.register_redirect_token, register_redirect_token))
        regist_status_key = find_key_by_value_regist_status(REGIST_STATUS.register_grant)
        registration.regist_status = regist_status_key
        registration.user = user
        register_access_token = dwlib.token_create_user(registration.registrant_callback, TOKEN_TYPE.access, user.id)
        register_access_validate = registration.registrant_request_scope #TODO need to expand here
        register_request_token = dwlib.token_create_user(registration.registrant_callback, TOKEN_TYPE.request, user.id)
        register_request_scope = ''
        registration.register_access_token = register_access_token
        registration.register_access_validate = register_access_validate
        registration.register_request_token = register_request_token
        registration.register_request_scope = register_request_scope
        registration.save()
        params = {
            url_keys.regist_status: REGIST_STATUS.registrant_confirm, # for mutual registraiton it is different, user need to decide here, TODO
            url_keys.regist_type: regist_type,
            url_keys.regist_callback: regist_callback_me,
            url_keys.registrant_request_token: registration.registrant_request_token,
            url_keys.register_access_token: register_access_token,
            url_keys.register_access_validate: register_access_validate,
            url_keys.register_request_token: register_request_token,
            url_keys.register_request_scope: register_request_scope,
            }
        url_params = dwlib.urlencode(params)
        url = '%s?%s'%(registration.registrant_callback, url_params)
        c = {
            'regist_grant_url': url,
            'register_request_action':{
                'label': url_keys.register_request_action,
                'request': url_keys.register_request_action_request,
                },
            'register_request_scope': {
                'label': url_keys.register_request_scope,
                'value': register_request_scope,
                },
            'register_request_token': {
                'label': url_keys.register_request_token,
                'value': register_request_token,
                },
            'register_access_token': {
                'label': url_keys.register_access_token,
                'value': register_access_token,
                },
            'register_access_validate': {
                'label': url_keys.register_access_validate,
                'value': register_access_validate,
                },
            'regist_status':{
                'label': url_keys.regist_status,
                'value': REGIST_STATUS.register_grant,
                },
            'regist_type':{ # need to add into template files
                'label': url_keys.regist_type,
                'value':regist_type,
                },
            }
        context = RequestContext(self.request, c)
        return render_to_response("regist_grant.html", context)
    def registrant_owner_redirect(self): pass
    def registrant_owner_grant(self): pass
    def registrant_confirm(self): pass
    def register_activate(self): 
        return method_register_activate(self.request)
    def regist_finish(self): pass
    
def regist(request):
    # if no correct status is matched
    return regist_steps(regist_dealer_resource(request), request)




    
