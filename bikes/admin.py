from django.contrib import admin
from .models import station, bike, rental
from .models import *

admin.site.register(user)
# admin.site.register(bike_user)
admin.site.register(station)
admin.site.register(bike)
admin.site.register(rental)

# Register your models here.
