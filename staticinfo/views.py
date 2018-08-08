from django.shortcuts import render, get_object_or_404
from rest_framework import generics

from .models import Page
from .serializers import PageSerializer, PageListSerializer

# Create your views here.

class PageList(generics.ListAPIView):
    serializer_class = PageListSerializer
    
    def get_queryset(self):
        queryset = Page.objects.filter(hidden = False)
        return queryset


class PageDetail(generics.RetrieveAPIView):
    serializer_class = PageSerializer
    model = Page

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, slug=self.kwargs['s'])
