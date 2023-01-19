from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
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

# https://docs.djangoproject.com/en/4.1/topics/auth/customizing/
class UserAccountManager(BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        """
        Creates and saves a superuser with the given username and password.
        """
        user = self.create_user(
            username,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser):
    is_face_recognition_enabled = models.BooleanField(default=False)
    is_twin = models.BooleanField(default=False)
    telephone = models.CharField(max_length=20)
    

    objects = UserAccountManager()

    REQUIRED_FIELDS = ['is_face_recognition_enabled', 'is_twin','telephone']

    def __str__(self):
        return self.get_username()

