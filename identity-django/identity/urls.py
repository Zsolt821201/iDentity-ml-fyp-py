from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordChangeView
from django.contrib import admin
from .import views
from .views import UserEditView, PasswordsChangeView


urlpatterns = [
    path('', views.index, name='index'),
    path('locations/', views.locations, name='locations'),
    path('locations/<int:location_id>/',views.location_details, name='details'),
    path('locations/<int:location_id>/<str:location_sign_in_date>/',views.location_roster_details, name='roster-details'),
    path('user-accounts/<int:user_account_id>/',views.user_account_details, name='user-account-details'),
    path("login/", views.login_user, name="login"),
    path("logout_user", views.logout_user, name="logout"),
    path('setup-facial-recognition/', views.setup_facial_recognition, name='setup_facial_recognition'),
    path('test/', views.test, name='test'),
    path('upload-facial-data/', views.upload_facial_data, name="upload-facial-data"),
    path('edit_user_profile/', UserEditView.as_view(), name="edit_user_profile"),
    path('change-password/', PasswordsChangeView.as_view(), name='change_password'),
    path('sign-in/<int:location_id>/', views.sign_in, name='sign_in'),
    path('perform-sign-in/', views.perform_sign_in, name='perform-sign-in'),
    path('identify-user-from-face/', views.identify_user_from_face, name='identify-user-from-face'),
    
    
    path('sign-out/<int:location_id>/', views.sign_out, name='sign_out'),
    path('force-sign-out/<int:roster_id>/', views.force_sign_out, name='force-sign-out'),
    
    path('perform-sign-out/', views.perform_sign_out, name='perform-sign-out'),
    path('remove-permission/<int:location_id>/<int:user_account_id>/', views.remove_permission, name='remove-permission'),
    
    
    
]
