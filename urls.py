from django.conf.urls.defaults import *
from trs.views import *
#from trs.views.place import *


#from trs_web.trs.views.place import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from trs.views.forms import PlaceForm
from trs.views.device import DeviceForm
import os
PROJECT_DIR = os.path.dirname(__file__)



urlpatterns =\
patterns('',
         # Example:
         # (r'^trs_web/', include('trs_web.foo.urls')),
         (r'^$', views.ticket_list),
         url(r'^ticket/(\d{1,6})/$', ticket.message_list, name="ticket"),
         (r'^edit_ticket/$', ticket.edit_ticket),
         #(r'^new_ticket/$', ticket.add_ticket),
         url(r'^create_ticket/for-user/(?P<user_id>\d{1,6})$', views.TicketCreate.as_view()),
         #url(r'^add_ticket/user/(\d{1,6})/(\w+)/$', ticket.add_ticket, name="new_ticket"),
         #url(r'^add_ticket/user/(?P<user_id>\d{1,6})/(?P<status>\w+)/$', ticket.TicketView.exec_save, name="new_ticket"),


         #url(r'^ticket/(?P<id>\d{1,6})/$', ticket.TicketView.exec_update, name="ticket"),

         #url(r'^user/(?P<id>\d{1,6})/$', user.UserView.exec_update, name="user"),
         url(r'^create_user$', views.UserCreate.as_view(), name="user_create"),
         url(r'^user/(?P<pk>\d+)/edit/$', views.UserUpdate.as_view(), name="user_update"),
         url(r'^create_(\w+)$', views.generic_create, name="create"),
         (r'^places/$', place.places),
         (r'^place/(\d{1,6})$', place.places),
         (r'^user_to_place/(\d{1,6})/(\d{1,6})$', views.user_to_place),
         #(r'^add_place/$', place.add_place),
         
         url(r'^add_ticket/user/(?P<user_id>\d{1,6})/(?P<status>\w+)/$', views.generic_create,name="add_ticket"),

         url(r'^edit_(\w+)/(\d{1,6})/$', views.generic_edit, name="edit"),
         (r'^delete_(\w+)/(\d{1,6})$', views.generic_delete),
         (r'^ajax/(\w+)/(\d{1,6})$', views.generic_jget),
         (r'^ajax/users$', views.ajax_users),

         (r'^validate/device/$', 'ajax_validation.views.validate', {'form_class': DeviceForm},
          'device_form_validate'),
         (r'^validate/place/$', 'ajax_validation.views.validate', {'form_class': PlaceForm},
          'device_form_validate'),

         (r'^del_place/(\d{1,6})$', place.del_place),

         (r'^doc_upload/$', place.doc_upload),
         (r'^search_users/$', views.search_users),
         (r'^ticket_reply/$', views.ticket_reply),
         (r'^login/$', views.login),
         (r'^logout/$', views.logout),
         url(r'^options/$', views.options, name="options"),
         url(r'^media/(?P<path>.*)$', "django.views.static.serve",
         {'document_root': os.path.join(PROJECT_DIR,"media") }
             ),

         # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
         # to INSTALLED_APPS to enable admin documentation:
         # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

         # Uncomment the next line to enable the admin:
         # (r'^admin/', include(admin.site.urls)),
         )
