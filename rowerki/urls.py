"""rowerki URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from django.http import HttpResponse
from django.shortcuts import render, redirect
import datetime
# from settings import *

def current_datetime(request):
    now = datetime.datetime.now()
    return render(request, 'bikes/base.html')
#    html = "<style>" + open(os.path.join(BASE_DIR, 'static/startbootstrap-bare-1.0.4/css/bootstrap.css')).read() + "</style>" + open(os.path.join(BASE_DIR, 'static/startbootstrap-bare-1.0.4/index.html')).read()
#    return HttpResponse(html)

def foo(request):
    return redirect('bikes:index')

urlpatterns = [
    url(r'^bikes/', include('bikes.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^.*', foo),
    url(r'^polls/', include('polls.urls')),
    url(r'^$', current_datetime),
]
