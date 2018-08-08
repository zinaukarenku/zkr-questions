import random

from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view

from darbai.models import Project
from darbai.serializers import ProjectSerializer
from nariai.models import Politician
from nariai.serializers import PoliticianSummarySerializer

#turbūt mandriausia ir sudėtingiausia platformos kodo dalis
#CARD_SETTINGS yra masyvas
#Šiame masyve aprašoma, kokios skirtingos kortelės turėtų būt pateikiamos per frontpage_init
#kiekviena masyvo dalis pakomentuota pirmajame masyvo naryje

CARD_SETTINGS = [
    {
        'name': 'politician', #pavadinimas, kuriuo objektas pateikiamas grąžinamame json'e
        'model': Politician, #modelis, pagal kurį sudaroma kortelė
        'serializer': PoliticianSummarySerializer, #serializeris, pagal kurį sudaroma kortelė
        'choices': [ #galimi kortelei parinkto objekto variantai
            #kiekvienas toks parinkimas išties nustato queryset, kurio pirmas objektas tada ir būna rodomas kortelėje
            {
                'title': 'Aktyviausias (-ia)', #Ką šis pasirinkimas parenka
                'order_by': '-activity', #pagal ką turėtume sortinti queryset'ą
                'query': {
                    'active': True, #kokie papildomi filtrai turėtų būti
                },
            },
            {
                'title': 'Neaktyviausias (-ia)',
                'order_by': 'activity',
                'query': {
                    'active': True,
                },
            },
            {
                'title': 'Efektyviausias (-ia)',
                'order_by': '-effectiveness',
                'query': {
                    'active': True,
                },
            },
            {
                'title': 'Neefektyviausias (-ia)',
                'order_by': 'effectiveness',
                'query': {
                    'active': True,
                },
            },
            {
                'title': 'Mažiausiai posėdžių praleidžiantis',
                'order_by': '-attendance',
                'query': {
                    'active': True,
                },
            },
            {
                'title': 'Daugiausiai posėdžių praleidžiantis',
                'order_by': 'attendance',
                'query': {
                    'active': True,
                },
            },
        ],
    },
    {
        'name': 'project',
        'model': Project,
        'serializer': ProjectSerializer,
        'choices': [
            {
                'title': 'Daugiausia balsų prieš gavęs',
                'order_by': '-votes_p',
                'query': {
                    'hidden': False,
                    },
            },
            {
                'title': 'Daugiausia balsų už gavęs',
                'order_by': '-votes_u',
                'query': {
                    'hidden': False,
                    },
            },
        ],
    }
]

# Create your views here.

#Šis view tiesiog pateikia visą frontendą naršyklei
def frontpage(request):
    return render(request, 'index.html')

#iš šio view frontendas gauna frontpage korteles
@api_view()
def frontpage_init(request):
    
    #ši funkcija kiekvienam CARD_SETTINGS masyvo nariui sugeneruoja kortelę pagal kortelės nustatymus
    def add_card(card_settings):
        card_choice = random.choice(card_settings['choices']) #parenkamas kortelės variantas iš choices
        card_queryset = card_settings['model'].objects.filter(**card_choice['query']) #sugeneruojamas queryset
        card_queryset = card_queryset.order_by(card_choice['order_by']) 
        card_object = card_queryset[0] #parenkamas pirmas objektas iš queryset
        return { #sugeneruojamas kortelės objektas
            'name': card_settings['name'],
            'title': card_choice['title'],
            'object': card_settings['serializer'](card_object).data,
        }

    return_object = {}
    return_object['cards'] = list(map(add_card, CARD_SETTINGS)) #šia eilute per visą CARD_SETTINGS masyvą paleidžiame add_card funkciją
    #taip iš esmės sugeneruojamas frontpage_init json'as

    return Response(return_object)
