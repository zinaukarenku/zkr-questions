from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.PoliticianList.as_view()), #visi aktyvūs seimo nariai
    url(r'^(?P<pk>[0-9]+)/$', views.PoliticianDetail.as_view()), #vieno politiko info
    url(r'^(?P<pk>[0-9]+)/summary/$', views.PoliticianSummary.as_view()), #vieno politiko sutrumpinta info
    url(r'^group/(?P<pk>[0-9]+)/?$', views.GroupDetail.as_view()), #grupės nariai
]
