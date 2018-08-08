from django.conf.urls import url

from . import views

app_name = 'klausimai'
urlpatterns = [
    url(r'json/init/$', views.init, name='jsonInit'),
    url(r'json/area/$', views.area, name='jsonArea'),
    url(r'json/party/$', views.party, name='jsonParty'),
    url(r'json/politician/$', views.politicianJson, name='jsonPolitician'),
    url(r'users/$', views.userRedir, name='userRedir'),
    url(r'approval/$', views.approval, name='approval'),
    url(r'answers/$', views.answers, name='answers'),
    url(r'comments/$', views.comments, name='comments'),
    url(r'latest/$', views.latest, name='latest'),
    url(r'latest/(?P<step>[0-9]+)/$', views.latestAdd, name='latestAdd'),
    url(r'latest/unanswered/$', views.latestUnans, name='latestUnans'),
    url(r'latest/unanswered/(?P<step>[0-9]+)/$', views.latestUnansAdd, name='latestUnansAdd'),
    url(r'latest/answered/$', views.latestAns, name='latestAns'),
    url(r'latest/answered/(?P<step>[0-9]+)/$', views.latestAnsAdd, name='latestAnsAdd'),
    url(r'question/(?P<pk>[0-9]+)/$', views.question, name='question'),
    url(r'politician/(?P<pk>[0-9]+)/$', views.politician, name='politician'),
    url(r'politician/(?P<pk>[0-9]+)/(?P<step>[0-9]+)/$', views.politicianAdd, name='politicianAdd'),
    url(r'politician/(?P<pk>[0-9]+)/unanswered/$', views.politicianUnans, name='politicianUnans'),
    url(r'politician/(?P<pk>[0-9]+)/unanswered/(?P<step>[0-9]+)/$', views.politicianUnansAdd, name='politicianUnansAdd'),
    url(r'politician/(?P<pk>[0-9]+)/answered/$', views.politicianAns, name='politicianAns'),
    url(r'politician/(?P<pk>[0-9]+)/answered/(?P<step>[0-9]+)/$', views.politicianAnsAdd, name='politicianAnsAdd'),
    url(r'promise/(?P<pk>[0-9]+)/$', views.promise, name='promise'),
    url(r'unsubscribe/$', views.unsubReg, name='unsubReg'),
    url(r'unsubscribe/(?P<pk>[0-9]+)/$', views.unsubUnreg, name='unsubUnreg'),
    url(r'resubscribe/', views.subReg, name='subReg'),
    url(r'^$', views.start, name='start'),
]
