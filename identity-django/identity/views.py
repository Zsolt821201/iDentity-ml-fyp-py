import cv2
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.forms import UserChangeForm
from django.http import HttpResponse
from .utilities import face_training, stream_image, detect_and_save_user_face
import numpy as numpy
from .models import Location, UserAccount
from django.contrib import messages
from django.shortcuts import  render, redirect
from django.views import generic
from PIL import Image
from django.contrib.sessions.models import Session

def index(request):
    return render(request, 'website/index.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, f"You are logged in as {username}.")
            return redirect('/locations/')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('/user-accounts/')
    else:
        messages.error(request,"Invalid username or password")
    
    return render(request, 'user-accounts/login.html')

def logout_user(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('user-accounts/login.html')           
        
class UserEditView(generic.UpdateView):
    form_class = UserChangeForm
    template_name = 'user-accounts/edit-user-profile.html'
    success_url = reverse_lazy('user-accounts/setup-facial-recognition.html')
    
    def get_object(self):
        return self.request.user
    

def locations(request):
    locations: list(Location) = Location.objects.order_by('-name')
    return render(request, 'locations/index.html', {'locations': locations})

def location_details(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'locations/details.html', {'location': location})

def setup_facial_recognition(request):
    return render(request, 'user-accounts/setup-facial-recognition.html', {'user_account_id': request.user.id})

def test(request):
    face_training()
    return render(request, 'user-accounts/test.html')

def facial_login(request):
    return render(request, 'user-accounts/facial-login.html')

def perform_facial_login(request):
    request_data = request.POST;
   
    image_bytes = stream_image(request_data['image-base64'])
    #image_number = request_data['image-number']

    open_cv_image = numpy.array(Image.open(image_bytes))

    if face_found:
        #user = authenticate(request, username=username, password=password)
    
    face_found = detect_and_save_user_face(session_user_account_id, open_cv_image, image_number)
    

@csrf_exempt
def upload_facial_data(request):
    request_data = request.POST;
    request_user_id = request_data['user-account-id']
    session_user_account_id = str(request.user.id)  # get loggedInUser

    if session_user_account_id != request_user_id:
        return HttpResponse('Unauthorized', status=401)
    
    _ = get_object_or_404(UserAccount, pk=session_user_account_id) # Confirm that the user exists
    
    image_bytes = stream_image(request_data['image-base64'])
    image_number = request_data['image-number']

    open_cv_image = numpy.array(Image.open(image_bytes))

    
    face_found = detect_and_save_user_face(session_user_account_id, open_cv_image, image_number)
    if face_found:
        return HttpResponse('OK', status=200)
    else:
        return HttpResponse('Error', status=418)#https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/418 I'm a teapot
    

