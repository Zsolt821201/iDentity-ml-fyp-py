from django.contrib import admin

from .models import Location, LocationPermission, Roster

admin.site.register(Location)
admin.site.register(LocationPermission)
admin.site.register(Roster)