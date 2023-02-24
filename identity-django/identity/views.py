from django.http import JsonResponse
from datetime import datetime
import cv2
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.sessions.models import Session
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from .forms import UserChangeForm
from .utilities import face_recognition_web, is_on_active_roster, is_permission_denied, parse_roaster_signing_requests, sign_in_at_location, sign_out_at_location
from .utilities import face_training
from .utilities import stream_image
from .utilities import detect_and_save_user_face
from .utilities import MyResponseCodes
import numpy as numpy
from .models import Location, LocationPermission, Roster, UserAccount
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import generic
from PIL import Image


class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'user-accounts/change-password.html'
    success_url = reverse_lazy('/locations/')


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
            return redirect('/login/')
    else:
        messages.error(request, "Invalid username or password")

    return render(request, 'user-accounts/login.html')


def logout_user(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('/login/')


class UserEditView(LoginRequiredMixin, generic.UpdateView):
    form_class = UserChangeForm
    template_name = 'user-accounts/edit-user-profile.html'
    success_url = reverse_lazy('edit_user_profile')

    def get_object(self):
        return self.request.user


@login_required
def locations(request):
    locations: list(Location) = Location.objects.order_by('-name')
    return render(request, 'locations/index.html', {'locations': locations})


@login_required
def location_details(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    location_active_sign_ins: list = Roster.objects.filter(
        location=location, sign_out_date__isnull=True)

    location_day_roster_logs: list = Roster.objects.filter(
        location=location).values_list('sign_in_date__date', flat=True).distinct()

    context = {
        'location': location,
        'location_active_sign_ins': location_active_sign_ins,
        'location_day_roster_logs': location_day_roster_logs,

    }
    return render(request, 'locations/details.html', context)


@login_required
def location_roster_details(request, location_id, location_sign_in_date):
    location = get_object_or_404(Location, pk=location_id)

    roster_list = location.roster_set.filter(
        sign_in_date__date=location_sign_in_date)

    context = {
        'location': location,
        'location_sign_in_date': location_sign_in_date,
        'roster_list': roster_list,
    }
    return render(request, 'locations/roster-details.html', context)


@login_required
def user_account_details(request, user_account_id):
    user_account = get_object_or_404(Location, pk=user_account_id)
    return render(request, 'user-accounts/user-details-profile.html', {'user_account': user_account})


@login_required
def setup_facial_recognition(request):
    user_account = get_object_or_404(UserAccount, pk=request.user.id)

    #TODO: Fix
    if not user_account.is_face_recognition_enabled:
        return render(request, 'user-accounts/setup-facial-recognition-denied.html', {'user_account_id': request.user.id})

    return render(request, 'user-accounts/setup-facial-recognition.html', {'user_account_id': request.user.id})


@login_required
def test(request):
    face_training()
    return render(request, 'user-accounts/test.html')


@login_required
def force_sign_out(_, roster_id):
    roster: Roster = Roster.objects.get(
        id=roster_id)
    roster.sign_out_date = datetime.now()
    roster.save()
    return redirect(f'/locations/{roster.location.id}')


@login_required
def remove_permission(_, location_id, user_account_id):
    instance: LocationPermission = LocationPermission.objects.get(
        location_id__id=location_id, user_account_id__id=user_account_id)
    instance.delete()
    return redirect(f'/locations/{location_id}')


@login_required
@permission_required('identity.activate_sign_in', raise_exception=True)
def sign_in(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'user-accounts/sign-in-new.html', {'location': location})


@login_required
@permission_required('identity.activate_sign_off', raise_exception=True)
def sign_out(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'user-accounts/sign-out.html', {'location': location})


@csrf_exempt
def perform_sign_in(request):
    face_found, user_id = parse_roaster_signing_requests(request)

    if not face_found:
        return HttpResponse('Error', status=MyResponseCodes.NO_FACE_FOUND)

    location_id = 1  # TODO Clean
    location = Location.objects.get(pk=location_id)
    user_account = UserAccount.objects.get(pk=user_id)

    if is_on_active_roster(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.ALREADY_ON_ROASTER)

    if is_permission_denied(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.LOCATION_PERMISSION_DENIED)

    sign_in_at_location(user_account, location)
    return HttpResponse('OK', status=200)


@csrf_exempt
def perform_sign_in1(request, location_id, user_account_id):

    location = Location.objects.get(pk=location_id)
    user_account = UserAccount.objects.get(pk=user_account_id)

    if is_on_active_roster(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.ALREADY_ON_ROASTER)

    if is_permission_denied(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.LOCATION_PERMISSION_DENIED)

    sign_in_at_location(user_account, location)
    return HttpResponse('OK', status=200)


@csrf_exempt
def identify_user_from_face(request):
    face_found, user_id = parse_roaster_signing_requests(request)

    if not face_found:
        return JsonResponse({'userId': 0})

    user_account = UserAccount.objects.get(pk=user_id)

    return JsonResponse({'userId': user_account.id, 'username': user_account.username, 'firstName': user_account.first_name, 'lastName': user_account.last_name, 'confidence': 100})





@csrf_exempt
def perform_sign_out(request):
    face_found, user_id = parse_roaster_signing_requests(request)

    if not face_found:
        return HttpResponse('Error', status=MyResponseCodes.NO_FACE_FOUND)

    location_id = 1  # TODO:clean
    location = Location.objects.get(pk=location_id)
    user_account = UserAccount.objects.get(pk=user_id)

    if not is_on_active_roster(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.NOT_ON_ROASTER)

    if is_permission_denied(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.LOCATION_PERMISSION_DENIED)

    sign_out_at_location(user_account, location)
    return HttpResponse('OK', status=200)


@csrf_exempt
def perform_sign_out1(request, location_id, user_account_id):
    location = Location.objects.get(pk=location_id)
    user_account = UserAccount.objects.get(pk=user_account_id)

    if not is_on_active_roster(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.NOT_ON_ROASTER)

    if is_permission_denied(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.LOCATION_PERMISSION_DENIED)

    sign_out_at_location(user_account, location)
    return HttpResponse('OK', status=200)



@csrf_exempt
def upload_facial_data(request):
    """ Receives a base64 encoded image for a user, detects a face saves the face to the system(folder on disk)

    Args:
        request (_type_): _description_

    Returns:
        HttpResponse : _description_
    """
    request_data = request.POST
    request_user_id = request_data['user-account-id']
    session_user_account_id = str(request.user.id)  # get loggedInUser

    if session_user_account_id != request_user_id:
        return HttpResponse('Unauthorized', status=401)

    # Confirm that the user exists
    _ = get_object_or_404(UserAccount, pk=session_user_account_id)

    image_bytes = stream_image(request_data['image-base64'])
    image_number = request_data['image-number']

    open_cv_image = numpy.array(Image.open(image_bytes))

    face_found = detect_and_save_user_face(
        session_user_account_id, open_cv_image, image_number)
    
    if face_found and image_number == '30':
        face_training()
    
    if face_found:
        return HttpResponse('OK', status=200)
    else:
        return HttpResponse('Error', status=MyResponseCodes.NO_FACE_FOUND)


def change_password(request):

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('/')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change-password.html', {
        'form': form
    })
