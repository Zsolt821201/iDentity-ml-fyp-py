from dataclasses import dataclass
import datetime
from numpy import ndarray
from pathlib import Path
import os
import sqlite3
from sqlite3 import Error

import cv2
import numpy
from PIL import Image
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
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    user_account_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


class Roster(models.Model):
    id = models.AutoField(primary_key=True)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    sign_in_date = models.DateTimeField('date signed in', auto_now_add=True)
    sign_out_date = models.DateTimeField(
        'date signed out', blank=True, null=True)
    user_account_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

class UserAccount(AbstractUser):
    is_face_recognition_enabled = models.BooleanField(default=False)
    is_twin = models.BooleanField(default=False)
    telephone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.get_username()
    
    # Add Update Method save user account  images to disk

    
