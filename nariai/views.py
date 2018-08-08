from django.shortcuts import render, get_object_or_404
from rest_framework import generics

from libzkr.filtering import filter_exclude_sort
from nariai.models import Politician, Group
from nariai.serializers import PoliticianSummarySerializer, PoliticianFullSerializer, GroupSerializer

# Create your views here.

#aktyvių seimo narių sąrašas
class PoliticianList(generics.ListAPIView):
    serializer_class = PoliticianSummarySerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Politician.objects.filter(active = True)
        queryset = filter_exclude_sort(queryset, self.request.GET)
        return queryset


#konkretaus politiko info
class PoliticianDetail(generics.RetrieveAPIView):
    model = Politician
    serializer_class = PoliticianFullSerializer

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


#konkretaus politiko sutraukta info
class PoliticianSummary(generics.RetrieveAPIView):
    model = Politician
    serializer_class = PoliticianSummarySerializer

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


#grupės info
class GroupDetail(generics.RetrieveAPIView):
    model = Group
    serializer_class = GroupSerializer

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])
