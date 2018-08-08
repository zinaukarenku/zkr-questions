from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def login_view(request, error=None):
    if request.method == 'GET':
        return render(request, 'login.html', context={'error': error})
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/admin/')
            else:
                return redirect('login_view')
        else:
            return redirect('login_view')


def logout_view(request):
    logout(request)
    return redirect('/')


def pw_reset_view(request):
    pass
