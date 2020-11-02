from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
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

def index(request, *args, **kwargs):
    
    return render(request, 'bikes/home.html')

def profile(request, *args, **kwargs):
    print (kwargs)
    # if request.method == "POST":
    #     print request.POST
    # print dir(request.user)
    if request.user.is_authenticated:
        # rental = get_object_or_404(Station, pk=station_id)
        kwargs.update({'rentals':request.user.user.rental_set.all().filter(end_station__isnull=True)})
    return render(request, 'bikes/profile.html', context=kwargs)

def rent_bike(station_id, bike_id, user):
    # try:
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
    # except:
    #     return ("error", "something went wrong, try again")

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
    try:
        with transaction.atomic():
            Rental.objects.select_for_update()
            Bike.objects.select_for_update()
            BikeUser.objects.select_for_update()
            rental = Rental.objects.get(pk=rental_id)
            if rental.end_station is not None or rental.end_date is not None:
                ("error", "Service already Canceled.")
            end_station = Station.objects.get(pk=station_id)
            rental.bike.station = end_station
            rental.bike.rental_id = None
            rental.end_station = end_station
            rental.end_date = datetime.now()
            charge = rental_charge(rental.end_date - rental.start_date)
            rental.cost = charge
            rental.user.balance -= charge
            rental.user.save()
            rental.save()
            rental.bike.save()
            return ("success", "Service Deliverd successfully. Charged user %d for the renal." % charge)
    except:
        return ("error", "Something went wrong, try again.")

def station_detail(request, station_id):
    if not request.user.is_authenticated:
        return redirect('bikes:login')
    if request.method == 'POST':
        station = get_object_or_404(Bike, pk=request.POST['b_id'])
        out = rent_bike(station_id, request.POST['b_id'], request.user.user)
        return profile(request, alerts=[out])
    station = get_object_or_404(Station, pk=station_id)
    return render(request, 'bikes/station_detail.html', context = {'station':station, 'bikes':station.bike_set.all().filter(rental__isnull=True).filter(working=True)})

def stations(request):
    if not request.user.is_authenticated:
        return redirect('bikes:login')
    if request.method == 'POST':
        print(request.POST)
        # print
        if 'return_station' in request.POST:
            # print '\n\nreturn bike\n'
            out = return_bike(request.POST['rental_id'], request.POST['station_id'])
            return profile(request, alerts=[out])
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
    if not request.user.is_authenticated:
        return redirect('bikes:login')
    rentals = request.user.user.rental_set.all().order_by('-end_date')[:5]
    if request.method == 'POST':
        print(request.POST)
        if "show_all_rentals" in request.POST:
            rentals = request.user.user.rental_set.all().order_by('-end_date')
        if "account_details_save" in request.POST:
            try:
                with transaction.atomic():
                    BikeUser.objects.select_for_update()
                    if request.POST['name'] != '':
                        request.user.user.name = request.POST['name']
                    if request.POST['surname'] != '':
                        request.user.user.surname = request.POST['surname']
                    if request.POST['name'] != '':
                        request.user.user.address = request.POST['address']
            except:
                pass
        if "change_password" in request.POST:
            if request.POST['new_password'] != request.POST['new_password2']:
                return render(request, 'bikes/details.html', {'rentals':rentals,'alerts':[('error', 'Passwords don\'t match.')]})
            if request.user.check_password(request.POST['old_password']):
                # try:
                    user = request.user
                    with transaction.atomic():
                        request.user.set_password(request.POST['new_password'])
                        print('before save', request.user)
                        print(request.user.is_authenticated())
                        request.user.save()
                        update_session_auth_hash(request, request.user)
                    return render(request, 'bikes/details.html', {'rentals':rentals,'alerts':[('success', 'Password changed successfully.')]})
                # except:
            else:
                return render(request, 'bikes/details.html', {'rentals':rentals,'alerts':[('error', 'Wrong password.')]})
            return render(request, 'bikes/details.html', {'rentals':rentals,'alerts':[('error', 'Something went wrong.')]})
    return render(request, 'bikes/details.html', {'rentals':rentals})


def logout_page(request):
    if not request.user.is_authenticated:
        return redirect('bikes:index')
    logout(request)
    return index(request, alerts = [('success', 'Logged out successfully!')])

def login_page(request):
    if request.user.is_authenticated:
        return redirect('bikes:profile')
    print(BikeUser.objects.all())
    if request.method == 'POST':
        if 'login_request' in request.POST:
            user = authenticate(username=request.POST['login'], password=request.POST['password'])
            print(user)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return index(request)
    return render(request, 'bikes/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('bikes:profile')
    if request.method == 'POST':
        print(request.POST)
        if 'register_request' in request.POST:
            try:
                User.objects.get(username=request.POST['login'])
                return render(request, 'bikes/register.html', context={'alerts':[('error', 'Username already taken')]})
            except:
                pass
            if request.POST['password'] != request.POST['password2']:
                print("passwords don't match")
                return render(request, 'bikes/register.html', context={'alerts':[('error', 'Passwords don\'t match')]})
            try:
                with transaction.atomic():
                    user = User(username=request.POST['login'])
                    user.set_password(request.POST['password'])
                    user.save()
                    bikeuser = BikeUser(user=user,
                                       login=request.POST['login'],
                                       address=request.POST['address'],
                                       name=request.POST['name'],
                                       surname=request.POST['surname'])
                    bikeuser.save()
                    return index(request, alerts=[('success', 'User created successfully. You can log into your new account!')])
            except:
                return redirect('bikes:register')
    return render(request, 'bikes/register.html')

def top_up(request):
    if not request.user.is_authenticated:
        return redirect('bikes:index')
    if request.method == 'POST':
        try:
            print(request.user.is_superuser)
            if  request.user.is_superuser:
                return render(request, 'bikes/top_up.html', context={'alerts':[('error', 'You don\'t have permission to do it, sorry.')]})
            if int(request.POST['amount']) < 0:
                return render(request, 'bikes/top_up.html', context={'alerts':[('error', 'Negative amount.')]})
            with transaction.atomic():
                BikeUser.objects.select_for_update()
                request.user.user.balance += int(request.POST['amount'])
                request.user.user.save()
        except:
            return render(request, 'bikes/top_up.html', context={'alerts':[("error", "something went wrong, try again")]})
    return render(request, 'bikes/top_up.html')

def rental_detail(request, rental_id):
    if not request.user.is_authenticated:
        return redirect('bikes:login')
    rentals = request.user.user.rental_set.all().order_by('-end_date')[:5]
    try:
        rental = Rental.objects.get(pk=rental_id)
        if request.user.user != rental.user:
            return render(request, 'bikes/profile.html', {'rentals':rentals, 'alerts':[('error', 'You cannot see this rental, sorry.')], 'rentals':request.user.user.rental_set.all().filter(end_station__isnull=True)})
        return render(request, 'bikes/rental_detail.html', {'rental':rental})
    except:
        return render(request, 'bikes/profile.html', {'rentals':rentals, 'alerts':[('error', 'Something went wrong, sorry.')], 'rentals':request.user.user.rental_set.all().filter(end_station__isnull=True)})

def faq(request):
    # print dir(request)
    print(request.get_raw_uri())
    if request.user.is_authenticated():
        return redirect('bikes:index')
    return render(request, 'bikes/lorem.html')

def terms(request):
    if request.user.is_authenticated():
        return redirect('bikes:index')
    return render(request, 'bikes/lorem.html')
