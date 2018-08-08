from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.http import HttpResponse

from .models import Registree

# Create your views here.

def pw_set_page(request, key):
    if request.user.is_authenticated():
        return redirect("/")
    try:
        registration = Registree.objects.get(key=key)
    except Exception:
        return redirect("/")
    newuser = registration.user
    return render(request, 'zkr_registration/pw_set.html', context={'key': key})

def pw_set_act(request):
    if not request.POST['key'] or not request.POST['newpw']:
        return redirect("/")
    try:
        registration = Registree.objects.get(key=request.POST['key'])
    except Exception:
        return redirect("/")
    registration.user.set_password(request.POST['newpw'])
    try:
        pol = registration.user.politician
        pol.is_registered = True
        pol.save()
    except Exception:
        pass
    registration.user.save()
    registration_set = Registree.objects.filter(user=registration.user)
    for reg in registration_set:
        reg.delete()
    return redirect("/")
