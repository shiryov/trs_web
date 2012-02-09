'''
Created on 14.07.2010

@author: boris
'''
from trs_web.trs.models import *
from trs.models import User

def session_user(request):
    login=request.session.get('login',None)
    if login:
        return User.objects.get(login=login)
    return None