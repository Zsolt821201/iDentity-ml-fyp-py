from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class LocationPermission(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    user_account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    
    def __str__(self):
        return f"{self.location.name} - {self.user_account.get_username()}"


class Roster(models.Model):
    id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    sign_in_date = models.DateTimeField('date signed in', auto_now_add=True)
    sign_out_date = models.DateTimeField('date signed out', blank=True, null=True)
    user_account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.location.name} - {self.sign_in_date.strftime('%Y-%m-%d %H:%M:%S')} - {self.user_account.get_username()}"


class UserAccount(AbstractUser):
    is_face_recognition_enabled = models.BooleanField(default=False)
    is_twin = models.BooleanField(default=False)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.get_username()

    # Add Update Method save user account  images to disk
