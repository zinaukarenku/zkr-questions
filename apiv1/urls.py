from django.conf.urls import url

from . import views, sec_views

app_name = 'api_v1'

#public urls
urlpatterns = [
    url(r'stats/$', views.stats, name='stats'),
    url(r'id/party/$', views.partyId, name='partyId'),
    url(r'id/politician/$', views.politicianId, name='politicianId'),
    url(r'id/area/$', views.areaId, name='areaId'),
    url(r'latest/$', views.latest, name='latest'),
    url(r'questiondump/$', views.question_dump, name="question_dump"),
    url(r'politicianinfo/(?P<pk>[0-9]+)/$', views.politicianInfo, name='politicianInfo'),
    url(r'expertInfo/(?P<pk>[0-9]+)/$', views.expertInfo, name='expertInfo'),
    url(r'partylist/$', views.partyList, name='partylist'),
    url(r'partyinfo/(?P<pk>[0-9]+)/$', views.partyInfo, name='partyInfo'),
    url(r'arealist/$', views.areaList, name='areaList'),
    url(r'areainfo/(?P<pk>[0-9]+)/$', views.areaInfo, name='areaInfo'),
    url(r'questioninfo/(?P<pk>[0-9]+)/$', views.questionInfo, name='questionInfo'),
    url(r'answerinfo/(?P<pk>[0-9]+)/$', views.answerInfo, name='answerInfo'),
    url(r'ask/$', views.askQuestion, name='askQuestion'),
]

#protected urls
urlpatterns += [
    url(r'sec/approval/$', sec_views.approval, name='approval'),
    url(r'sec/promise/$', sec_views.newpromise, name='new_promise'),
    url(r'sec/update/$', sec_views.update, name='update'),
    url(r'sec/bio_change/$', sec_views.bio_change, name='bio_change'),
    url(r'sec/answer/$', sec_views.answer, name='answer'),
    url(r'sec/comment/$', sec_views.comment, name='comment'),
]
