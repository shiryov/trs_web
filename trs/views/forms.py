# -*- coding: utf8 -*-
'''
Created on 05.08.2010

@author: boris
'''
from django import forms
from django.forms import ModelForm,HiddenInput
from trs_web.trs.models import *
from trs.models import Ticket, User, Place


class TicketFilterForm(forms.Form):
    CHOICES = ((u'hide', 'скрыть'), (u'my', 'только мои'), (u'all', 'все'),)
    #  admins=User.objects.filter(admin=True)
    #  for a in admins:
    #     CHOICES.append((unicode(a.id),a.name))
    
    new = forms.BooleanField(label='Новые', required=False)
    accepted = forms.ChoiceField(label='Принятые', choices=CHOICES, required=False)
    closed = forms.ChoiceField(label='Закрытые', choices=CHOICES, required=False)
    deleted = forms.ChoiceField(label='Удалённые', choices=CHOICES, required=False)    
    wreport = forms.BooleanField(label='Только с отчётами', required=False)

class PlaceDocumentForm(forms.Form):
    name = forms.CharField(max_length=50, required=False)
    comment = forms.CharField(max_length=100, required=False)    
    file = forms.FileField(required=True)
    place_id = forms.IntegerField(widget=forms.HiddenInput)  
    doc_id = forms.IntegerField(widget=forms.HiddenInput, required=False)


class PlaceForm(ModelForm):  
    parent = forms.IntegerField(widget = HiddenInput())
    def clean_parent(self):
        if self.cleaned_data['parent'] != None:
            return Place.objects.get(id=self.cleaned_data['parent'])  
    class Meta:
        model = Place        
        #exclude = ('parent',)

class TicketForm(ModelForm):
    def user_tickets(self):
        if self.instance.user:
            return Ticket.objects.filter(user=self.instance.user).order_by('-id')
        else:
            return None
        
    class Meta:
        model = Ticket
        exclude = ( 'user', 'admin', 'device', 'ctime', 'closing_time')

        
