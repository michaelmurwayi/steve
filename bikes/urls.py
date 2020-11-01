from django.conf.urls import url

from . import views

app_name = 'bikes'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile/', views.profile, name='profile'),
    url(r'^station/(?P<station_id>[0-9]+)/$', views.station_detail, name='station_detail'),
    url(r'^rental/(?P<rental_id>[0-9]+)/$', views.rental_detail, name='rental_detail'),
    url(r'^details$', views.details, name='details'),
    url(r'^stations/$', views.stations, name='stations'),
    url(r'^login$', views.login_page, name='login'),
    url(r'^logout$', views.logout_page, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^topup$', views.top_up, name="top_up"),
    url(r'^faq$', views.faq, name="faq"),
    url(r'^terms$', views.terms, name="terms"),
]
