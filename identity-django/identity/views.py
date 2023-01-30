import cv2
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.forms import AuthenticationForm 
from django.http import HttpResponse
from numpy import ndarray
from .models import Location, UserAccount, get_user_face
from django.contrib import messages
from django.shortcuts import  render, redirect
from PIL import Image

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
            return redirect('locations/index.html')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('user-accounts/login.html')
    else:
            messages.error(request,"Invalid username or password")
    
    return render(request, 'user-accounts/login.html')

def logout_user(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('user-accounts/login.html')           
        


def locations(request):
    locations: list(Location) = Location.objects.order_by('-name')
    return render(request, 'locations/index.html', {'locations': locations})

def location_details(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'locations/details.html', {'location': location})

def setup_facial_recognition(request):
    return render(request, 'user-accounts/setup-facial-recognition.html')

def test(request):
   return render(request, 'user-accounts/test.html')

def test_client_using_server(request):
   video_capture = cv2.VideoCapture(0)
   while True:
       _, img = video_capture.read()
       cv2.imshow('camera', img)

@csrf_exempt
#@api_view(['POST'])
def upload_facial_data(request):
    request_data = request.POST;
    
    request_user_id = request_data['user-account-id']
    
    # get loggedInUser
    session_user_account_id = '1'

    if session_user_account_id != request_user_id:
        return HttpResponse('Unauthorized', status=401)
    
    _ = get_object_or_404(UserAccount, pk=session_user_account_id)
    
    request_image =  request.POST['image']
    image_number = request_data['image-number']
    print(f"image_number: {image_number}")

    print(str(request_image))
    #image = cv2.imdecode(np.fromstring(request_image.read(), np.uint8), cv2.IMREAD_UNCHANGED)

    import numpy as np
    pil_img = Image.open(request_image)
    cv_img = np.array(pil_img)

    #image = np.frombuffer(request_image, np.uint8)

    
    success = get_user_face(session_user_account_id, cv_img, image_number)
    if success:
        return HttpResponse('OK', status=200)
    else:
        return HttpResponse('Error', status=500)

            
def upload_facial_data2(request):
    data = request.data
    # get loggedInUser
    user_account_id:int = 1

    if user_account_id != data['user-account-id']:
        return HttpResponse('Unauthorized', status=401)
    
    user_account = get_object_or_404(UserAccount, pk=user_account_id)
    face_images = data['images']
    user_account.is_face_recognition_enabled = True
    UserAccount.save(user_account, face_images)
    
    face_count: int = 0
    
    for face_image in face_images:
        image_path: str = f"{DATABASE_FACE_DIRECTORY}/user.{user_account_id}.{face_count}.jpg"
        cv2.imwrite(image_path, face_image)

    return HttpResponse('OK', status=200)
    

