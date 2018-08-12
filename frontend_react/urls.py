from django.urls import path

from frontend_react.views import frontpage
from . import views

urlpatterns = [
    path(r'', frontpage),
]
