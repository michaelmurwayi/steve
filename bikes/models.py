from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User# as authUser#, AbstractBaseUser
from django.core.exceptions import ValidationError

# Create your models here.

class user(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=30)
    login = models.CharField(unique=True, max_length=200)
    balance = models.IntegerField(default=0)
    in_debt = models.BooleanField(default=False)
    name = models.CharField(max_length=30, blank=False)
    surname = models.CharField(max_length=30, blank=False)
    email = models.EmailField()
    reg_date = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        self.in_debt = (self.balance < 0)
        super(user, self).save(*args, **kwargs)
    def __str__(self):
        return self.login

class station(models.Model):
    address = models.CharField(max_length=200)
    capacity = models.IntegerField()
    working = models.BooleanField(default=True)
    def __str__(self):
        return str(self.id) + ' - ' + self.address

class bike(models.Model):
    station = models.ForeignKey(station, null=True, blank=True, on_delete=models.SET_NULL)
    rental = models.ForeignKey('rental', related_name='rental', null=True, blank=True, on_delete=models.CASCADE)
    working = models.BooleanField(default=True)
    def clean(self):
        if self.rental:
            self.station = None
        if self.station:
            self.rental = None
    def __str__(self):
        return str(self.id)

class rental(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    bike = models.ForeignKey(bike, related_name='bike', on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, default=None)
    start_station = models.ForeignKey(station, related_name = "start_station", on_delete=models.CASCADE)
    end_station = models.ForeignKey(station, null=True, related_name = "end_station", on_delete=models.CASCADE)
    def clean(self):
        if start_date >= end_date:
            raise ValidationError('rental ended before start')
    def __str__(self):
        return str(self.id)
