from django.conf.urls import url, include

from . import views
#from frontend.views import frontpage_init

#čia tiesiog centrinis taškas visiems /api/v2/ url'ams

urlpatterns = [
    #url(r'init/', frontpage_init),
    url(r'user/$', views.CurrentUserView.as_view()),
    url(r'nariai/', include('nariai.urls')),
    url(r'darbai/', include('darbai.urls')),
    url(r'apie/', include('staticinfo.urls')),
]
