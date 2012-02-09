# -*- coding: utf8 -*-
from datetime import datetime
import os
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response, redirect
from trs.models import Device, Document, Place, DocFile
from trs.views.device import DeviceForm
from trs.views.forms import PlaceForm, PlaceDocumentForm
from trs.views.helpers import session_user

__author__ = 'boris'

def places(request, id=22):
    try:
        id = int(id)
    except ValueError:
        raise Http404()
    item = Place.objects.get(id=id)
    root = Place.objects.get(id=22)
    form = PlaceDocumentForm()
    place_form = PlaceForm()
    device_form = DeviceForm()
    docs = Document.objects.filter(place=item)
    # places = Place.objects.all()
    devices = Device.objects.filter(place=item)

    def li(item, idpref):
        res = '<li id="' + idpref + str(item.id) + '">'
        res += '<a href="' + item.get_absolute_url() + '">' + item.name + '</a>'
        res += '<ul>'
        for c in item.childs():
            res += li(c, idpref)
            #print li(c,idpref)
        res += '</ul>'
        res += '</li>'
        return res

    return render_to_response('places.html',
                              {'tree': li(root, 'place_'),
                               'root': item, 'docs': docs, 'form': form,
                               'place_form': place_form, 'device_form': device_form,
                               'devices': devices})


#def add_place(request):
#    parent_id = 0
#    try:
#        par = Place.objects.get(id=request.POST.get('parent_id'))
#        parent_id = par.id
#        p = Place(parent=par)
#        form = PlaceForm(request.POST, instance=p)
#        form.save(commit=True)
#    except:
#        None
#    return redirect('/place/' + str(parent_id))
#
def del_place(request, place_id=None):
    parent_id = 0
    try:
        place_id = int(place_id)
        parent_id = Place.objects.get(id=place_id).parent.id
        Place.objects.get(id=place_id).delete()
    except ValueError:
        raise Http404()

    return redirect('/place/' + str(parent_id))

#-------------------------------------Document upload
INPUT_PATH = "d:/input"

def gen_filename(fname):
    if not os.path.exists(INPUT_PATH + '/' + fname):
        return fname
    else:
        spl = fname.rsplit('.', 1)
        name = spl[0]
        ext = spl[1]
        fname = name + '_.' + ext
        return gen_filename(fname)

def doc_upload(request):
    if request.method == 'POST':
        form = PlaceDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            #return HttpResponse(str(cd))
            place = Place.objects.get(id=cd['place_id'])
            #doc = None
            #title = None
            #Существущий документ (обновляем название)
            if cd['doc_id'] is not None:
                doc = Document.objects.get(id=int(cd['doc_id']))
                if cd['name'] != '':
                    doc.name = cd['name']
                    doc.save()
            #Новый документ
            else:
                title = cd['name'] if cd['name'] != '' else request.FILES['file'].name
                doc = Document(name=title, place=place)
                doc.save()
                #Создаём DocFile
            doc_file = DocFile(document=doc, version=0, file_name='temp',
                               comment=cd['comment'],
                               ctime=datetime.datetime.now(),
                               user=session_user(request))
            doc_file.save()
            #id.ext

            fname = str(doc_file.id) + '.' + request.FILES['file'].name.rsplit('.', 1)[1]
            doc_file.file_name = fname
            doc_file.save()
            #Сохраняем файл
            destination = open(INPUT_PATH + '/' + fname, 'wb+')
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
            destination.close()
            return redirect('/place/' + str(cd['place_id']))
        else:
            return HttpResponse(str(form.errors))


  