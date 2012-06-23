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
#from libauth.views import method_regist_init, method_registrant_request, method_register_owner_redirect, method_register_owner_grant, method_register_grant, method_regist_finish

def hello(request):
    return HttpResponse('hello, resource')

regist_callback_me = 'http://localhost:8001/resource/regist'

class regist_dealer_resource(regist_dealer):
    def regist_init(self): pass
    def registrant_request(self): 
        pass
    def register_owner_redirect(self):
        return method_register_owner_redirect(self.request, regist_callback_me)
    def register_owner_grant(self): 
        return method_register_owner_grant(self.request, regist_callback_me)
    def register_grant(self): 
        return method_register_grant(self.request, regist_callback_me)
    def registrant_owner_redirect(self): pass
    def registrant_owner_grant(self): pass
    def registrant_confirm(self): pass
    def register_activate(self): 
        return method_register_activate(self.request)
    def regist_finish(self): 
        return method_regist_finish(self.request)
    
def regist(request):
    # if no correct status is matched
    return regist_steps(request, regist_callback_me)

