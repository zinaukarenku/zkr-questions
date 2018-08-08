from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.PageList.as_view()),
    path(r'<slug:s>/', views.PageDetail.as_view()),
]
