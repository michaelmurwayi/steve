from django.conf.urls import url

from . import views

app_name = 'bikes'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^station/(?P<station_id>[0-9]+)/$', views.station_detail, name='station_detail'),
    url(r'^stations/$', views.stations, name='stations'),
]
