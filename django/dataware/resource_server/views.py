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
from libauth.views import regist_steps

def hello(request):
    return HttpResponse('hello, resource')

regist_callback_me = 'http://localhost:8001/resource/regist'
    
def regist(request):
    # if no correct status is matched
    return regist_steps(request, regist_callback_me)

