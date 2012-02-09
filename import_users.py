# -*- coding: utf8 -*-
'''
Created on 26.05.2010

@author: boris
'''
import os
os.environ['DJANGO_SETTINGS_MODULE']='settings'
from trs.models import *

f=open('D:\its.csv','r')
for line in f.readlines():
    data=line.split(';')
    if len(data)>1:
        name=data[0]
        email=data[10]
        phone=data[6]        
        if name=='ДЭМ':
            name=name+' '+data[2]+' '
        
        u=User(name=name,email=email,phone=phone)        
        u.save()
        print (name+' '+email+' '+phone)

