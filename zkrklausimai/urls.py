"""zkrklausimai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

# from frontend.views import frontpage
from django.urls import path

from frontend.admin import main_admin
from . import views

urlpatterns = [
    path('admin/', main_admin.urls),
    url(r'login/?$', views.login_view, name='login_view'),
    url(r'logout/?$', views.logout_view),
    url(r'^api/v1/', include('apiv1.urls')),
    url(r'^api/v2/', include('apiv2.urls')),
    url(r'^registration/', include('zkr_registration.urls')),
    url(r'^', include('frontend_react.urls')),
]
