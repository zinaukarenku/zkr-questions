from django.shortcuts import render, get_object_or_404
from rest_framework import generics, pagination

from libzkr.filtering import filter_exclude_sort
from .models import Project, Vote
from .serializers import ProjectSerializer, ProjectVoteSerializer

#===PAGINATION===

#Pagination taisyklės pagrindiniam projektų sąrašui
class ProjectListPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 30


# Create your views here.

#projektų overall sąrašas
class ProjectList(generics.ListAPIView):
    serializer_class = ProjectSerializer
    pagination_class = ProjectListPagination

    def get_queryset(self):
        #queryset = Project.objects.exclude(hidden = True)
        #surandam visus naujausius kiekvieno metacode projektus
        qu1 = Project.objects.raw("select b.id from (select metacode, max(date_start) as m, count(*) as ct from darbai_project group by metacode) as a inner join darbai_project as b on (a.metacode=b.metacode and a.m=b.date_start);")
        #pagal juos parenkame actual projektus kurių mums reikia
        #darydami taip, gaunam normalų QuerySet vietoj RawQuerySet
        queryset = Project.objects.filter(id__in=[a.id for a in qu1]).order_by("-schedule_entries__date")
        #ši funkcijikė labai gražiai susitvarko su GET parametrais
        #gaunam gražų API ^^
        #žiūrėti libzkr
        queryset = filter_exclude_sort(queryset, self.request.GET)
        return queryset

#vieno kažkurio projekto duomenys
class ProjectVotes(generics.RetrieveAPIView):
    model = Project
    serializer_class = ProjectVoteSerializer

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])
