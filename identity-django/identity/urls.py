from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
   # path('login/', views.login, name='login'),
   # path('logout/', views.logout, name='logout'),
    #path('change-password/', views.change_password, name='change_password'),
    #path('roaster-logs/', views.roaster_logs, name='roaster_logs'),
    path('setup-facial-recognition/', views.setup_facial_recognition, name='setup_facial_recognition'),
    path('locations/', views.locations, name='locations'),
    path('test/', views.test, name='test'),
    path('locations/<int:location_id>/',views.location_details, name='details'),
    path('upload-facial-data/', views.upload_facial_data, name="upload-facial-data"),
]
