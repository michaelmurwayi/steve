from django.contrib import admin
from custom_user.admin import EmailUserAdmin
from .models import bike_user

AUTH_USER_MODEL = 'bikes.bike_user'
