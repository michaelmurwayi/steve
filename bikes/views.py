from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
# from django.template import Template, Context
from datetime import datetime, timedelta

from django.db import transaction

from .models import rental as Rental, bike as Bike, user as BikeUser, station as Station
from django.contrib.auth.models import User

from .forms import *

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

# Create your views here.

def index(request, *args, **kwargs):
    print kwargs
    # if request.method == "POST":
    #     print request.POST
    # print dir(request.user)
    if request.user.is_authenticated():
        kwargs.update({'rentals':request.user.user.rental_set.all().filter(end_station__isnull=True)})
    return render(request, 'bikes/index.html', context=kwargs)

def rent_bike(station_id, bike_id, user):
    try:
        if user.in_debt:
            return ("error", "user in debt, top-up account before you can rent a bike")
        with transaction.atomic():
            bike = Bike.objects.select_for_update().get(pk=bike_id)
            if bike.rental is not None:
                return ("error", "somebody already rented that bike, try with some other")
            station = Station.objects.select_for_update().get(pk=station_id)
            if len(user.rental_set.all().filter(end_station__isnull=True)) >= 3:
                return ("error", "you already rented 3 bikes")
            r = Rental(user = user, bike = bike, start_date = datetime.now(), start_station = station)
            r.save()
            bike.rental = r
            bike.save()
        return ("success", "bike rented successfully")
    except:
        return ("error", "something went wrong, try again")

from math import ceil
def rental_charge(duration):
    if(duration < timedelta()):
        raise Exception("negative rental duration")
    # current payment scheme
    # first 20 minutes - free of charge
    _free = timedelta(minutes=20)
    # first hour - 2
    _first_hour = 2
    # each next hour - 4
    _hour = 4
    # each next day - 150
    _day = 150
    h = timedelta(hours=1)
    d = timedelta(days=1)
    return 0 if duration <= _free else (ceil((duration - d).total_seconds() / d.total_seconds()) * _day +
            ceil((duration - h).total_seconds() / h.total_seconds()) * _hour +
            _first_hour)

def return_bike(rental_id, station_id):
    # try:
        with transaction.atomic():
            Rental.objects.select_for_update()
            Bike.objects.select_for_update()
            BikeUser.objects.select_for_update()
            rental = Rental.objects.get(pk=rental_id)
            end_station = Station.objects.get(pk=station_id)
            rental.bike.station = end_station
            rental.bike.rental_id = None
            rental.end_station = end_station
            rental.end_date = datetime.now()
            charge = rental_charge(rental.end_date - rental.start_date)
            rental.user.balance -= charge
            rental.user.save()
            rental.save()
            rental.bike.save()
        return ("success", "bike returned successfully")
    # except:
    #     return ("error", "something went wrong, try again")

def station_detail(request, station_id):
    if request.method == 'POST':
        s = get_object_or_404(Bike, pk=request.POST['b_id'])
        out = rent_bike(station_id, request.POST['b_id'], request.user.user)
        return index(request, alerts=[out])
    s = get_object_or_404(Station, pk=station_id)
    return render(request, 'bikes/station_detail.html', context = {'station':s, 'bikes':s.bike_set.all().filter(rental__isnull=True).filter(working=True)})

def stations(request):
    if request.method == 'POST':
        print request.POST
        # print
        if 'return_station' in request.POST:
            # print '\n\nreturn bike\n'
            out = return_bike(request.POST['rental_id'], request.POST['station_id'])
            return index(request, alerts=[out])
        if 'station_select' in request.POST:
            return redirect('bikes:station_detail', station_id=request.POST['station_id'])
        if 'bike_return' in request.POST:
            s = {'stations':Station.objects.all()}
            s.update(request.POST)
            # print s['rental_id']
            s['rental_id'] = int(s['rental_id'][0])
            return render(request, 'bikes/stations.html', context = s)
            pass
        # print reverse('bikes:station_detail', kwargs={'station_id':request.POST['s_id']})
    return render(request, 'bikes/stations.html', context = {'stations':Station.objects.all()})

def details(request):
    return render(request, 'bikes/base.html')


def logout_page(request):
    logout(request)
    print 'redirected to index'
    return index(request, alerts = [('success', 'logged out successfully')])

def login_page(request):
    print BikeUser.objects.all()
    # form = BikeLoginForm()
    if request.method == 'POST':
        if 'login_request' in request.POST:
            user = authenticate(username='bikes_'+request.POST['login'], password=request.POST['password'])
            print user
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return index(request)
        # form = BikeLoginForm(request.POST)
        # print '\n\n\n\nprocessed form'
        # if form.is_valid():
        #     print form.fields
    return render(request, 'bikes/login.html')

def register(request):
    if request.method == 'POST':
        print request.POST
        if 'register_request' in request.POST:
            if request.POST['password'] != request.POST['password2']:
                print "passwords don't match"
                return redirect('bikes:register')
            try:
                with transaction.atomic():
                    user = User(username='bikes_'+request.POST['login'])
                    user.set_password(request.POST['password'])
                    user.save()
                    bikeuser = BikeUser(user=user,
                                       login=request.POST['login'],
                                       address=request.POST['address'],
                                       name=request.POST['name'],
                                       surname=request.POST['surname'])
                    bikeuser.save()
                    return redirect('bikes:index')
            except:
                return redirect('bikes:register')
    return render(request, 'bikes/register.html')
