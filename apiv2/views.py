from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics

from .serializers import UserSerializer

# Create your views here.

class CurrentUserView(generics.RetrieveAPIView):
    model = User
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
