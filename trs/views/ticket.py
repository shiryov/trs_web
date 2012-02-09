# -*- coding: utf8 -*-
from datetime import datetime
from django.forms.models import ModelForm
from django.forms.widgets import HiddenInput
from django.forms.fields import IntegerField
from django.http import Http404
from django.shortcuts import render_to_response, redirect
import mail_fetcher
from trs.views.helpers import session_user
from trs.views.views import login_required

from views import View
from trs.models import Ticket, Message, User

__author__ = 'boris'

class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        exclude = ( 'user', 'admin', 'device', 'ctime', 'closing_time')


class TicketView(View):
    model_class = Ticket
    form_class = TicketForm

    def fill_initial_instance(self):

        self.instance.user = User.objects.get(id=int(self.request_params['user_id']))
        if self.request_params.get('status', '') == 'new':
            self.instance.status = '00'
        if self.request_params.get('status', '') == 'accepted':
            self.instance.status = '10'
            self.instance.accept_by(self.session_user)
        if self.request_params.get('status', '') == 'closed':
            self.instance.status = '30'
            self.instance.accept_by(self.session_user)
            self.instance.closing_time = datetime.now()
        self.instance.priority = '20'


    def get_templvars_onsave(self):
        ticket_user = self.instance.user

        tickets = Ticket.objects.filter(user=ticket_user).order_by('-id')
        return {'foruser': ticket_user, 'mode': self.request_params['status'],
                'tickets': tickets}

    def get_templvars_onupdate(self):
        ticket_user = self.instance.user

        tickets = Ticket.objects.filter(user=ticket_user).order_by('-id')
        return {'foruser': ticket_user, 'mode': self.instance.status,
                'tickets': tickets}

    def update_valid(self):
        old_status = self.instance.status
        new_status = self.form.data['status']
        mail_error = None
        t = self.form.save(commit=False)
        if t.is_new(old_status) and not t.is_new(new_status):
            if self.session_user:
                t.accept_by(self.session_user)
        if not t.is_new(old_status) and t.is_new(new_status) and t.admin:
            t.admin = None
            t.closing_time = None
        if not t.is_closed(old_status) and t.is_closed(new_status):
            t.closing_time = datetime.now()
        return View.update_valid(self)


#
@login_required
def message_list(request, ticket_id):
    try:
        ticket_id = int(ticket_id)
    except ValueError:
        raise Http404()
    t = Ticket.objects.get(id=ticket_id)
    form = TicketForm(instance=t)

    return render_to_response('message_list.html',
                              {'msgs': Message.objects.filter(
                                      ticket=t).order_by('-time'), 'ticket': t,
                               'form': form})

@login_required
def edit_ticket(request, ticket_id):
    """
    если метод GET - показываем форму, с содержимым объекта
    если POST и ticket_id != None - update
    """
    t = Ticket.objects.get(id=int(ticket_id))
    model_name = "Ticket"
    form_class = TicketForm
    admin = session_user(request)

    if request.method == 'GET':
        if ticket_id is not None:
            return render_to_response("%s_form.html" % model_name.lower(),
                                      {'form': form_class(instance=t)})
    elif request.method == 'POST':
        form = form_class(request.POST, instance=t)

        old_status = t.status
        new_status = form.data['status']
        mail_error = None
        try:
            form.save(commit=False)
            if t.is_new(old_status) and not t.is_new(new_status):
                if admin:
                    t.accept_by(admin)
            if not t.is_new(old_status) and t.is_new(new_status) and t.admin:
                t.admin = None
                t.closing_time = None
            if not t.is_closed(old_status) and t.is_closed(new_status):
                t.closing_time = datetime.datetime.now()
                #mail_error = mail_fetcher.send_ticket_closed_message(t)

            t.save()
        except ValueError:
            return render_to_response("%s_form.html" % model_name.lower(),
                                      {'msgs': Message.objects.filter(ticket=t)
                                       ,
                                       'ticket': t, 'form': form})
        if mail_error is not None:
            return render_to_response("%s_form.html" % model_name.lower(),
                                      {'msgs': Message.objects.filter(ticket=t)
                                       ,
                                       'ticket': t, 'form': form,
                                       'mail_error': mail_error})
    return redirect('ticket', t.id)

@login_required
def add_ticket(request, user_id=None, mode=None):
    if request.method == 'GET':
        try:
            user_id = int(user_id)
        except ValueError:
            raise Http404()
        admin = session_user(request)
        ticket_user = User.objects.get(id=user_id)
        ticket = Ticket()
        ticket.priority = '20'
        if not mode: mode = 'none'
        if mode == 'new': ticket.status = '00'
        if mode == 'accepted':
            ticket.admin = admin
            ticket.status = '10'
        if mode == 'closed':
            ticket.admin = admin
            ticket.status = '30'
        form = TicketForm(instance=ticket)
        tickets = Ticket.objects.filter(user=ticket_user).order_by('-id')
        return render_to_response('add_ticket.html',
                                  {'form': form, 'foruser': ticket_user,
                                   'mode': mode, 'tickets': tickets})
    else:
        admin = session_user(request)
        #TODO: make hidden fields and modify form.save method
        user = User.objects.get(id=request.POST.get('user_id'))
        t = Ticket(user=user)
        form = TicketForm(request.POST, instance=t)
        #---
        send_closed = False
        mail_error = None
        try:
            form.save(commit=False)
            if not t.is_new():
                if admin:
                    t.accept_by(admin)
            if t.is_closed():
                t.accept_by(admin)
                t.closing_time = datetime.datetime.now()
                send_closed = True
            t.save()
            mail_error = mail_fetcher.send_new_ticket_message(t, '')
            if send_closed:
                mail_error = mail_fetcher.send_ticket_closed_message(t)
        except ValueError:
            return render_to_response('add_ticket.html',
                                      {'form': form, 'foruser': user})
        if mail_error is not None:
            return render_to_response('add_ticket.html',
                                      {'form': form, 'foruser': user,
                                       'mail_error': mail_error})
        return redirect('/')