from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordChangeView
from django.contrib import admin
from .import views
from .views import UserEditView


urlpatterns = [
    path('', views.index, name='index'),
    path('locations/', views.locations, name='locations'),
    path('locations/<int:location_id>/',views.location_details, name='details'),
    path("login/", views.login_user, name="login"),
    path("logout_user", views.logout_user, name="logout"),
    path('setup-facial-recognition/', views.setup_facial_recognition, name='setup_facial_recognition'),
    path('test/', views.test, name='test'),
    path('upload-facial-data/', views.upload_facial_data, name="upload-facial-data"),
    path('edit_user_profile/', UserEditView.as_view(), name="edit_user_profile"),
    path('change-password/', PasswordChangeView.as_view(template_name='change_password.html'), name='change_password'),
    path('sign-in/<int:location_id>/', views.sign_in, name='sign_in'),
    path('perform-sign-in/', views.perform_sign_in, name='perform-sign-in'),
   
    
    
]
