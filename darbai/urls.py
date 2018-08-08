from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ProjectList.as_view()), #projektų overall sąrašas
    url(r'^(?P<pk>[0-9]+)/$', views.ProjectVotes.as_view()), #vieno kažkurio projekto duomenys
]
