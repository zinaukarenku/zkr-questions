from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.main_render, {'page':'stebek'}),
    path(r'stebek/', views.main_render, {'page':'stebek'}),
    path(r'apie/', views.main_render, {'page':'apie'}),
    path(r'apie/<slug>/', views.main_render, {'page':'apie'}),
]
