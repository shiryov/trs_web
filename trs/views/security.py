# -*- coding: utf8 -*-
'''
Created on 20.08.2010

@author: boris
'''
from django.shortcuts import render_to_response, redirect

PLACE_ADD = 10
PLACE_EDIT = 15
PLACE_DELETE =17
DOC_ADD = 20
DOC_EDIT = 30
DOC_DELETE = 40
DEVICE_ADD = 50
DEVICE_EDIT = 60
DEVICE_DELETE = 70
USER_ATTR_EMAIL = 1000

#роли:
ROOT=()
EMAIL_EDITOR=(USER_ATTR_EMAIL)


USER_ROLE={"bo" : [ROOT],'maxim':[EMAIL_EDITOR]}


def check_generic(view,mode):
    def tmp(*args, **kwargs):        
        login = False
        try:
            request = args[0];
            model_name = args[2];
            login = request.session.get('login', None)
        except:
            pass
        if not login:
            return render_to_response('login.html')
        else :       
            #kwargs['user']=User.objects.get(login=login)
            return view(*args, **kwargs)
    return tmp    
    