from django.forms.models import ModelForm
from django.http import Http404
from django.shortcuts import redirect, render_to_response
from trs.models import User
from trs.views.views import login_required, View

__author__ = 'boris'

class UserForm(ModelForm):
    class Meta:
        model = User


class UserView(View):
    model_class = User
    form_class = UserForm

@login_required
def user(request, id=None):
    if request.method == 'GET':
        try:
            id = int(id)
        except ValueError:
            raise Http404()
        u = User.objects.get(id=id)
        form = UserForm(instance=u)
        return render_to_response('user_form.html', {'user': u, 'form': form})
    if request.method == 'POST':
        id = request.POST.get('user_id', '')

        if id:
            instance = User.objects.get(id=id)
        else:
            instance = User()
        form = UserForm(request.POST, instance=instance)
        try:
            form.save(commit=False)
            instance.save()
        except ValueError:
            return render_to_response('user_form.html',
                                      {'user': instance, 'form': form})

        return redirect('user', instance.id)