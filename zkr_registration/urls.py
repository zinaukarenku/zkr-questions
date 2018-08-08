from django.conf.urls import url
from . import views

app_name='zkr_registration'
urlpatterns = [
    url(r'new/(?P<key>[0-9A-Za-z\+\_]+)/$', views.pw_set_page, name='pwSetPage'),
    url(r'reg_act/$', views.pw_set_act, name='pwSet'),
]
