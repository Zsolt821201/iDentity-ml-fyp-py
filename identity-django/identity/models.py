from django.conf import settings
from django.db import models

class Location(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)
    telephone = models.CharField(max_length=20)

class LocationPermission(models.Model):
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    user_account_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
        

class Roster(models.Model):
    id = models.AutoField(primary_key=True)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    sign_in_date = models.DateTimeField('date signed in', auto_now_add=True)
    sign_out_date = models.DateTimeField('date signed out', auto_now_add=True)
    user_account_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

