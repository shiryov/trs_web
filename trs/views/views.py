# -*- coding: utf8 -*-
import json
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView


from trs.models import *

import sys
import mail_fetcher

from forms import *

from device import *


def login_required(view):
    def tmp(*args, **kwargs):
        login = False
        try:
            request = args[0]
            login = request.session.get('login', None)
        except:
            pass
        if not login:
            return render_to_response('login.html')
        else:
        #kwargs['user']=User.objects.get(login=login)
            return view(*args, **kwargs)

    return tmp



class UserCreate(CreateView):
    form_class=UserForm
    template_name='user_form.html'
    success_url='/'

class UserUpdate(UpdateView):
    form_class=UserForm
    template_name='user_form.html'
    success_url='/'
    model=User




def ticket_filter(data, admin_id):
    res = Q()
    if data['new'] is True:
        res = res | Q(status='00')
    if data['accepted'] and data['accepted'] != 'hide':
        q = Q(status='10') | Q(status='20')
        if data['accepted'] == 'my':
            q = q & Q(admin__id=admin_id)
        res = res | q
    if data['closed'] and data['closed'] != 'hide':
        q = Q(status='30')
        if data['closed'] == 'my':
            q = q & Q(admin__id=admin_id)
        res = res | q
    if data['deleted'] and data['deleted'] != 'hide':
        q = Q(status='40')
        if data['deleted'] == 'my':
            q = q & Q(admin__id=admin_id)
        res = res | q
    return res


#################  Views #####################

@login_required
def ticket_list(request):
    admin = session_user(request)


    tickets = Ticket.objects.all().order_by('status', 'priority', '-ctime').filter(status__gt='20')
    tickets_open = Ticket.objects.all().order_by('status', 'priority', '-ctime').filter(status__lte='20')
    try:
        f = request.session['ticket_filter']
        filt = ticket_filter(f, admin.id)
        print filt
        tickets = tickets.filter(filt)
    except:
        pass

    
    paginator = Paginator(tickets, 25)

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        tickets = paginator.page(page)
    except (EmptyPage, InvalidPage):
        tickets = paginator.page(paginator.num_pages)

    return render_to_response('ticket_list.html', {'tickets': tickets,'tickets_open':tickets_open})




def user_to_place(request, id_user, id_place):
    try:
        id_user = int(id_user)
        id_place = int(id_place)
    except ValueError:
        raise Http404()
    place = Place.objects.get(id=id_place)
    user = User.objects.get(id=id_user)
    if user.place is not None:
        return render_to_response('error.html',
                                  {'short': "Неправильный пользователь",
                                   'msg': u"Пользователю %s уже назначено место %s" % (
                                   user.name,
                                   user.place.parent.name + '-->' + user.place.name)})

    user.place = place
    user.save()
    return redirect(place.get_absolute_url())


#Отправка ответа пользователю по почте
@login_required
def ticket_reply(request):
    if request.method == 'POST':
        msg_text = request.POST.get('msg_txt', '')
        ticket_id = request.POST.get('ticket_id', '')
        if msg_text and ticket_id:
            #mail_error = None
            ticket = Ticket.objects.get(id=ticket_id)
            mail_error = mail_fetcher.send_ticket_reply_message(ticket,
                                                                msg_text)

            if mail_error is None:
                message = Message(time=datetime.datetime.now(), ticket=ticket,
                                  text=msg_text, reply=True,
                                  user=ticket.user)
                message.save()
            return redirect('ticket', ticket_id)
            #return render_to_response('message_list.html', {'msgs': Message.objects.filter(ticket=ticket), 'ticket':ticket})


@login_required
def search_users(request):
    if request.method == 'POST':
        email = request.POST.get('srch_email', '')
        lastname = request.POST.get('srch_lastname', '')
        users = User.objects.filter(name__icontains=lastname,
                                    email__icontains=email).order_by("name")
        return render_to_response('search_users.html', {'users': users})
    else:
        return render_to_response('search_users.html')

        # @login_required
        # def add_ticket(request):
        # ticket=Ticket()
        # form=TicketForm(instance=ticket)
        # return render_to_response('add_ticket.html',{'form':form})


def login(request):
    if request.method == 'GET':
        if request.session.get('login', False):
            return render_to_response('ticket_list.html',
                                      {'tickets': Ticket.objects.all()})
        else:
            return render_to_response('login.html')
    if request.method == 'POST':
        try:
            u = User.objects.get(login__exact=request.POST['login'])
            if u.password == request.POST['password']:
                request.session['login'] = u.login
            return redirect('/')
        except User.DoesNotExist:
            return redirect('/login/')


@login_required
def options(request):
    if request.method == 'GET':
        filter_form = TicketFilterForm()
        try:
            filter_form = TicketFilterForm(request.session['ticket_filter'])
        except KeyError:
            pass
        return render_to_response('options.html', {'filter_form': filter_form})
    if request.method == 'POST':
        filter_form = TicketFilterForm(request.POST)

        if filter_form.is_valid():
            data = filter_form.cleaned_data
            request.session['ticket_filter'] = data
            print 'hello'
            return redirect('options')
        else:
            return HttpResponse('re' + str(filter_form.errors))


def logout(request):
    try:
        del request.session['login']
    except KeyError:
        pass
    return redirect('/login/')


#----------------------------------Generic CRUDs
def generic_edit(request, model_name,id):
    model = getattr(sys.modules['trs_web.trs.models'], model_name.capitalize())
    inst = model.objects.get(id=int(id))

    if request.method == 'GET':
        form = getattr(sys.modules['trs_web.trs.views.forms'],
                   model_name.capitalize() + 'Form')(instance=inst)
        return render_to_response(
                "%s_form.html" % model_name,{'form':form,})
    elif request.method == 'POST':
        form = getattr(sys.modules['trs_web.trs.views.forms'],
                   model_name.capitalize() + 'Form')(request.POST,
                                                     instance=inst)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse ('edit',args=[model_name,inst.id,]))
        else:
            return render_to_response("%s_form.html" % model_name,{'form':form,})

def ticket_create(request,user_id,status):
    try:
        user_id = int(user_id)
    except ValueError:
        raise Http404()
    admin = session_user(request)
    ticket_user = User.objects.get(id=user_id)
    ticket = Ticket()
    ticket.priority = '20'
    ticket.user=ticket_user
    if not status: status = 'none'
    if status == 'new': ticket.status = '00'
    if status == 'accepted':
        ticket.admin = admin
        ticket.status = '10'
    if status == 'closed':
        ticket.admin = admin
        ticket.status = '30'
    return generic_create(request,"ticket",init_instance=ticket,redirect=reverse ('create',args=["ticket",ticket.id,]))

class TicketCreate(CreateView):
    form_class=TicketForm
    success_url="/"
    template_name="ticket_form.html"

    def form_valid(self,form):
        admin = session_user(self.request)
        ticket_user = User.objects.get(id=self.kwargs['user_id'])
        ticket=form.save(commit=False)

        ticket.user=ticket_user
        if not ticket.status: ticket.status = 'none'
        if ticket.status == 'new': ticket.status = '00'
        if ticket.status == 'accepted':
            ticket.admin = admin
            ticket.status = '10'
        if ticket.status == 'closed':
            ticket.admin = admin
            ticket.status = '30'
        ticket.save()
        return redirect(self.get_success_url())

        



def generic_create(request, model_name, init_instance=None,redirect=None):
    if init_instance is None:
        init_instance=getattr(sys.modules['trs_web.trs.models'], model_name.capitalize())()
    if request.method == 'GET':
        form = getattr(sys.modules['trs_web.trs.views.forms'],
                   model_name.capitalize() + 'Form')(instance=init_instance)
        return render_to_response(
                "%s_form.html" % model_name,{'form':form,})
    if request.method == 'POST':
        form = getattr(sys.modules['trs_web.trs.views.forms'],
                   model_name.capitalize() + 'Form')(request.POST,instance=init_instance)
        if form.is_valid():
            form.save(commit=True)
            return redirect
        else:
            return "hello"


def generic_jget(request, model_name, id):
    try:
        id = int(id)
    except ValueError:
        raise Http404()
    model_name = model_name.capitalize()

    model = getattr(sys.modules['trs_web.trs.models'], model_name)
    inst = model.objects.get(id=id)
    return HttpResponse(serializers.serialize("json", [inst]))


def generic_delete(request, model_name, id):
    try:
        id = int(id)
    except ValueError:
        raise Http404()
    model = getattr(sys.modules['trs_web.trs.models'], model_name.capitalize())
    inst = model.objects.get(id=id)
    inst.delete()
    return redirect(inst.get_absolute_url())


#----------------------------Ajax

def ajax_users(request):
    name = request.GET.get('name', 'none')
    users = User.objects.filter(name__icontains=name)
    #    persons=Person.objects.all()
    list = []
    for e in users:
        list.append({'id': e.id, 'name': e.name})
    return HttpResponse(json.dumps(list))
