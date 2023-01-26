import cv2
from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse
from numpy import ndarray
from .models import Location, UserAccount, get_user_face

def index(request):
    return render(request, 'website/index.html')


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


def upload_facial_data(request):
    data = request.data
    # get loggedInUser
    user_account_id:int = 1

    if user_account_id != data['user-account-id']:
        return HttpResponse('Unauthorized', status=401)
    
    _ = get_object_or_404(UserAccount, pk=user_account_id)
    
    image = data['image']
    image_number = data['image-number']

    
    success = get_user_face(user_account_id, image, image_number)
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
    

