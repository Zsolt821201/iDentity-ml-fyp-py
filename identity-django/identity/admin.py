from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission


from .models import Location
from .models import LocationPermission
from .models import Roster
from .models import UserAccount

class UserAccountAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'is_twin', 'is_face_recognition_enabled', 'telephone'
        )
    # For Editing  a User
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
    # For Inserting a User
    add_fieldsets  = (
        (None, {
            'fields': ('username', 'password1', 'password2')
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
admin.site.register(Permission)
