from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import Location, LocationPermission, Roster, UserAccount

class UserAccountAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'is_twin', 'is_face_recognition_enabled', 'telephone'
        )
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'telephone', 'is_twin')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 
                'is_face_recognition_enabled',
                'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        })
    )
    
    add_fieldsets  = (
        (None, {
            'fields': ('password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'telephone', 'is_twin')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 
                'is_face_recognition_enabled',
                'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        })
    )
    



#
# Site Registrations
#

admin.site.register(Location)
admin.site.register(LocationPermission)
admin.site.register(Roster)
admin.site.register(UserAccount, UserAccountAdmin)  



