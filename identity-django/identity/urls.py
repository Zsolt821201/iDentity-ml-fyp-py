from django.urls import path
from django.contrib.auth import views as auth_views
from .import views
from .views import UserEditView


urlpatterns = [
    path('', views.index, name='index'),
    path('facial-login', views.facial_login, name='facial-login'),
    path('perform-facial-login', views.perform_facial_login, name='perform-facial-login'),
    path('locations/', views.locations, name='locations'),
    path('locations/<int:location_id>/',views.location_details, name='details'),
    path("login/", views.login_user, name="login"),
    path("logout_user", views.logout_user, name="logout"),
    path('setup-facial-recognition/', views.setup_facial_recognition, name='setup_facial_recognition'),
    path('test/', views.test, name='test'),
    path('upload-facial-data/', views.upload_facial_data, name="upload-facial-data"),
    path('edit_user_profile/', UserEditView.as_view(), name="edit_user_profile"),
    
]
