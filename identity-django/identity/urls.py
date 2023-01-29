from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path("login_user", views.login_user, name="login"),
    path('setup-facial-recognition/', views.setup_facial_recognition, name='setup_facial_recognition'),
    path('locations/', views.locations, name='locations'),
    path('test/', views.test, name='test'),
    path('locations/<int:location_id>/',views.location_details, name='details'),
    path('upload-facial-data/', views.upload_facial_data, name="upload-facial-data"),
]
