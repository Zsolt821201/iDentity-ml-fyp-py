from datetime import datetime
import cv2
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.forms import UserChangeForm
from django.http import HttpResponse
from .utilities import face_recognition_web
from .utilities import face_training
from .utilities import stream_image
from .utilities import detect_and_save_user_face
import numpy as numpy
from .models import Location, Roster, UserAccount
from django.contrib import messages
from django.shortcuts import  render, redirect
from django.views import generic
from PIL import Image
from django.contrib.sessions.models import Session
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

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
    return redirect('/login/')           
        
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

def sign_in(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'user-accounts/sign-in.html', {'location': location})

@csrf_exempt
def perform_sign_in(request):
    #//TODO: Implement facial login
    request_data = request.POST
   
    image_bytes = stream_image(request_data['image-base64'])
    location_id = request_data['location-id']
    location = Location.objects.get(pk=location_id)
    #image_number = request_data['image-number']

    open_cv_image = numpy.array(Image.open(image_bytes))

    user_id, confidence = face_recognition_web(open_cv_image)
    
    
    
    face_found = confidence > 70 # TODO: define system confidence level
    if face_found:
        user_account = UserAccount.objects.get(pk=user_id)
        # TODO: Permission Check
        sign_in_at_location(user_account, location)
        return HttpResponse('OK', status=200)    
    else:
        return HttpResponse('Error', status=418)#https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/418 I'm a teapot
    
def sign_in_at_location(user_account: UserAccount, location: Location):
    sign_in_date = datetime.now()
    roster:Roster = Roster(user_account_id=user_account, location_id=location, sign_in_date=sign_in_date)
    roster.save()
    

@csrf_exempt
def upload_facial_data(request):
    request_data = request.POST
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
    

def password_change(request):
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('change_password_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change-password.html', {
        'form': form
    })