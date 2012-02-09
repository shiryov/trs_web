# -*- coding: utf8 -*-
'''
Created on 14.07.2010

@author: boris
'''

from django import forms
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponse,Http404
from django.shortcuts import render_to_response, redirect
from django.template import Context
from django.template.loader import get_template

from trs_web.trs.models import *
from django.core import serializers
import datetime
import os
from helpers import *
from django import forms
from django.forms import ModelForm,HiddenInput
from trs_web.trs.models import *
#from forms import *  

#serializers.serialize("json", [Place.objects.get(id=22)])
from trs.models import Device, Place

class DeviceForm(ModelForm):
    place = forms.IntegerField(widget = HiddenInput())
    def clean_place(self):
        if self.cleaned_data['place'] != None:
            return Place.objects.get(id=self.cleaned_data['place'])
    class Meta:
        model = Device
   

def add(request):    
    parent_id=0
#    try:        
    #par=Place.objects.get(id=request.POST.get('parent_place_id'))     
    #p=Device(place=par)
    
    form=DeviceForm(request.POST)
    if form.is_valid():
        form.save(commit=True)
    else:
        return HttpResponse(form.errors)
#    except:
#        None        
    return redirect('/places/')

def jget(request,id=None):
    try:
        id = int(id)
    except ValueError:
        raise Http404()    
    device=Device.objects.get(id=id)
    return HttpResponse(serializers.serialize("json",[device]))
