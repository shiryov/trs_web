# -*- coding: utf8 -*-
'''
Created on 25.05.2010

@author: boris
'''
import os
import getpass, poplib
import re
from email import message_from_string
from email.utils import parseaddr
from email.header import Header,decode_header
from email.mime.text import MIMEText
import string
import smtplib
from datetime import *
os.environ['DJANGO_SETTINGS_MODULE']='settings'
from trs.models import *
from django.template.loader import get_template
from django.template import Context


def get_or_add_user(email,name):
    u=None
    try:
        u=User.objects.get(email=email)
    except User.DoesNotExist:
        u=User(email=email,name=name)
        u.save()
##    finally:
##        if u.name!=name:
##            u.name=name
##            u.save()
    return u

def send_message(from_,to,subject,text):
    msg=MIMEText(text,_charset='utf-8')
    msg['From'] = from_
    msg['To'] = to
    msg['Subject'] = Header(subject,'utf-8')    
#    msg['X-
#    msg.set_charset('utf-8')
    s = smtplib.SMTP('10.146.21.1')
    s.login('it@apmessv.amur.ru','1111')
    s.sendmail('it@apmessv.amur.ru', to, msg.as_string())
    s.quit()
    
        

def send_new_ticket_message(ticket,init_message):
    t = get_template('new_ticket_msg.txt')   
    msg_text=t.render(Context({'ticket':ticket}))
    mail_error=None
    try:
        send_message(from_='it@apmessv.amur.ru',to=ticket.user.email,
                 subject="Обращение № %05d зарегистрировано" % ticket.id,
                 text=msg_text.encode('utf-8'))
    except Exception,v:               
        mail_error=str(v)        
    return mail_error
        

def send_ticket_closed_message(ticket):
    t = get_template('ticket_closed_msg.txt')   
    msg_text=t.render(Context({'ticket':ticket}))
    mail_error=None
    try:
        send_message(from_='it@apmessv.amur.ru',to=ticket.user.email,
                     subject="Обращение № %05d выполнено" % ticket.id,                 
                     text=msg_text.encode('utf-8'))
    except Exception,v:
        mail_error=str(v)
    return mail_error

def send_ticket_reply_message(ticket,msg_text):
    templ = get_template('admin_reply_msg.txt')
    reply_templ=templ.render(Context({'ticket':ticket,'msg_text':msg_text}))
    mail_error=None
    try:
        send_message('it@apmessv.amur.ru',ticket.user.email,
                      "Re: Обращение № %05d" % ticket.id,                                      
                      reply_templ.encode('utf-8'))
    except Exception,v:
        mail_error=str(v)
    return mail_error
        
    
def process_message(text,from_=None,name=None,ticket_no=None):    
    msg=Message()
    msg.text=text
    new_ticket=None
    if from_ != None:
        msg.user=get_or_add_user(from_,name)
        if ticket_no == None:
            new_ticket = Ticket(priority='20',status='00',
                                ctime=datetime.datetime.now(),user=msg.user,description=msg.text)
            new_ticket.save()
            msg.ticket=new_ticket
            send_new_ticket_message(new_ticket,msg)
        else:
            msg.ticket=Ticket.objects.get(id=ticket_no)
    msg.save()
    return new_ticket

def check_mailbox(): 

    M = poplib.POP3('10.146.21.1')
    M.user('it@apmessv.amur.ru')
    M.pass_('Woo2ohtu')

    numMessages = len(M.list()[1])

    for i in range(numMessages):
        message=message_from_string(string.join(M.retr(i+1)[1], "\n"))
        counter = 1
        texts=[]        
        for part in message.walk():
            if part.get_content_maintype() == 'text' and part.get_content_subtype()=='plain':
                charset=part.get_content_charset(failobj='koi8-r')
                texts.append(unicode(part.get_payload(decode=True),charset))

        (name,email)=parseaddr(message['from'])
        (hdr,charset)=(decode_header(name))[0]
        #print hdr
        if charset != None:
            from_name=unicode(hdr,charset)
        else:
            from_name=hdr

        process_message(from_=email,name=from_name,text=string.join(texts,"\n"))
        
        #print string.join(texts,"\n")
        #print from_name
        M.dele(i+1)

        
    M.quit()


if __name__ == '__main__':
    check_mailbox()



