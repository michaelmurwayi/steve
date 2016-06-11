from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from datetime import datetime
# from django.template import Template, Context

from django.db import transaction

from .models import *

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

def index(request, kwargs={}):
    if request.method == "POST":
        print request.POST
    user_id = 1
    kwargs['rentals'] = user.objects.get(pk=1).rental_set.all().filter(end_station__isnull=True)
    print kwargs
    return render(request, 'bikes/index.html', context=kwargs)

def rent_bike(station_id, bike_id, user_id):
    try:
        with transaction.atomic():
            user_id = 1
            rbike = bike.objects.select_for_update().get(pk=bike_id)
            if rbike.rental is not None:
                return 'somebody already rented that bike, try with some other'
            rstation = station.objects.select_for_update().get(pk=station_id)
            ruser = user.objects.select_for_update().get(pk=user_id)
            if len(ruser.rental_set.all()) >= 3:
                return 'you already rented 3 bikes'
            r = rental(user = ruser, bike = rbike, start_date = datetime.now(), start_station = rstation)
            r.save()
            rbike.rental = r
            rbike.save()
        return 'bike rented successfully'
    except:
        return 'something went wrong, try again'

def return_bike(rental_id, station_id):
    # try:
        with transaction.atomic():
            rental.objects.select_for_update()
            crental = rental.objects.get(pk=rental_id)
            estation = station.objects.get(pk=station_id)
            print '\n\ncharge user for the rental\n\n'

            ##############################
            # charge user for the rental #
            ##############################

            crental.bike.station = estation
            crental.bike.rental_id = None
            crental.end_station = estation
            crental.end_date = datetime.now()
            crental.save()
            crental.bike.save()
        return 'bike returned successfully'
    # except:
    #     return 'something went wrong, try again'

def station_detail(request, station_id):
    if request.method == 'POST':
        s = get_object_or_404(bike, pk=request.POST['b_id'])
        print 'successfully locked'
        print s, request.POST['b_id']
        print rent_bike(station_id, request.POST['b_id'], None)
        return redirect('bikes:index')
    print request
    s = get_object_or_404(station, pk=station_id)
    return render(request, 'bikes/station_detail.html', context = {'station':s, 'bikes':s.bike_set.all().filter(rental__isnull=True).filter(working=True)})

# def stations_return(request, bike_id):

def stations(request):
    if request.method == 'POST':
        print request.POST
        print
        if 'return_station' in request.POST:
            print '\n\nreturn bike\n'
            print return_bike(request.POST['rental_id'], request.POST['station_id'])
            return redirect('bikes:index')
        if 'station_select' in request.POST:
            return redirect('bikes:station_detail', station_id=request.POST['station_id'])
        if 'bike_return' in request.POST:
            s = {'stations':station.objects.all()}
            s.update(request.POST)
            print s['rental_id']
            s['rental_id'] = int(s['rental_id'][0])
            return render(request, 'bikes/stations.html', context = s)
            pass
        # print reverse('bikes:station_detail', kwargs={'station_id':request.POST['s_id']})
    return render(request, 'bikes/stations.html', context = {'stations':station.objects.all()})
