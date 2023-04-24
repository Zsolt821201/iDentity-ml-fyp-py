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
from .utilities import is_on_active_roster, is_permission_denied, parse_roaster_signing_requests, sign_in_at_location, sign_out_at_location
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
    '''custom password change view. for updating a user's password.'''
    form_class = PasswordChangeForm
    template_name = 'user-accounts/change-password.html'
    success_url = reverse_lazy('/locations/')


def index(request):
    '''Index view, renders the home page of the website.'''
    return render(request, 'website/index.html')


def login_user(request):
    '''Handles user login by verifying the user's credentials and logging them in if they are valid.'''
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
    '''Logs out the user and redirects them to the login page.'''
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('/login/')


class UserEditView(LoginRequiredMixin, generic.UpdateView):
    '''custom user edit view. for updating a user's profile.'''
    form_class = UserChangeForm
    template_name = 'user-accounts/edit-user-profile.html'
    success_url = reverse_lazy('edit_user_profile')
# Retrieves the current user's information to pre-populate the form

    def get_object(self):
        return self.request.user


@login_required
def locations(request):
    '''Display a list of all locations.'''
    locations: list(Location) = Location.objects.order_by('-name')
    return render(request, 'locations/index.html', {'locations': locations})


@login_required
def location_details(request, location_id):
    '''Display detailed information about a specific location.'''
    location = get_object_or_404(Location, pk=location_id)
    # Get a list of currently active sign-ins for the location
    location_active_sign_ins: list = Roster.objects.filter(
        location=location, sign_out_date__isnull=True)
    # Get a list of distinct dates for which roster logs exist for the location
    location_day_roster_logs: list = Roster.objects.filter(
        location=location).values_list('sign_in_date__date', flat=True).distinct()
    # Prepare the context for rendering the template
    context = {
        'location': location,
        'location_active_sign_ins': location_active_sign_ins,
        'location_day_roster_logs': location_day_roster_logs,
    }

    return render(request, 'locations/details.html', context)


@login_required
def location_roster_details(request, location_id, location_sign_in_date):
    '''Display detailed information about a specific location's roster log for a specific date.'''
    location = get_object_or_404(Location, pk=location_id)
    # Retrieve the roster list for the specified location and date
    roster_list = location.roster_set.filter(
        sign_in_date__date=location_sign_in_date)
    # Prepare the context for rendering the template
    context = {
        'location': location,
        'location_sign_in_date': location_sign_in_date,
        'roster_list': roster_list,
    }
    return render(request, 'locations/roster-details.html', context)


@login_required
def user_account_details(request, user_account_id):
    '''Display detailed information about a specific user account.'''
    user_account = get_object_or_404(UserAccount, pk=user_account_id)
    return render(request, 'user-accounts/user-details-profile.html', {'user_account': user_account})


@login_required
def setup_facial_recognition(request):
    '''Handles the setup of facial recognition for the logged in user.'''
    user_account = get_object_or_404(UserAccount, pk=request.user.id)

    #TODO: Fix
    if not user_account.is_face_recognition_enabled:
        return render(request, 'user-accounts/setup-facial-recognition-denied.html', {'user_account_id': request.user.id})

    return render(request, 'user-accounts/setup-facial-recognition.html', {'user_account_id': request.user.id})


@login_required
def test(request):
    '''Trigers the facial recognition training process. and renders the test page.'''
    face_training()
    return render(request, 'user-accounts/test.html')


@login_required
def force_sign_out(_, roster_id):
    '''Forces a sign out for a specific roster entry.'''
    roster: Roster = Roster.objects.get(
        id=roster_id)
    roster.sign_out_date = datetime.now()
    roster.save()
    return redirect(f'/locations/{roster.location.id}')


@login_required
def remove_permission(request, location_id, user_account_id):
    '''Removes location permissions for a specific user account.'''
    user_account = get_object_or_404(UserAccount, pk=request.user.id)
    if hasPermission(user_account, location_id, 'identity.remove_permission'):
        instance: LocationPermission = LocationPermission.objects.get(
            location__id=location_id, user_account__id=user_account_id)
        instance.delete()
        return redirect(f'/locations/{location_id}')
    else:
        return render(request, 'user-accounts/permission-denied.html', {'user_account_id': request.user.id})


def hasPermission(user_account: UserAccount, location_id: int, permission: str):
    # TODO: Test
    return True
    # return LocationPermission.objects.filter(location_id__id=location_id, user_account_id__id=user_account.id, permission=permission).exists()


@login_required
@permission_required('identity.activate_sign_in', raise_exception=True)
def sign_in(request, location_id):
    '''Renders the sign in page for a specific location.'''
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'user-accounts/sign-in-new.html', {'location': location})


@login_required
@permission_required('identity.activate_sign_off', raise_exception=True)
def sign_out(request, location_id):
    '''Renders the sign out page for a specific location.'''
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'user-accounts/sign-out.html', {'location': location})


@csrf_exempt
@permission_required('identity.activate_sign_in', raise_exception=True)
def perform_sign_in(request):
    '''Perform the sign in based on facial recognition.'''
    face_found, user_id = parse_roaster_signing_requests(request)

    if not face_found:
        return HttpResponse('Error', status=MyResponseCodes.NO_FACE_FOUND)

    location_id = 1  # TODO Clean
    location = Location.objects.get(pk=location_id)
    user_account = UserAccount.objects.get(pk=user_id)
    # Check if the user is already on the active roster or if permission is denied
    if is_on_active_roster(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.ALREADY_ON_ROASTER)

    if is_permission_denied(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.LOCATION_PERMISSION_DENIED)
    # Sign in the user at the specified location
    sign_in_at_location(user_account, location)
    return HttpResponse('OK', status=200)


@csrf_exempt
def perform_sign_in1(request, location_id, user_account_id):
    '''Perform sign in based on user accoutn id and location id.(alternative method )'''
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
    '''Identify the user from the face and return their information'''
    face_found, user_id = parse_roaster_signing_requests(request)

    if not face_found:
        return JsonResponse({'userId': 0})
    # Retrieve the user account object
    user_account = UserAccount.objects.get(pk=user_id)
    # Return the user's information in a JSON response
    return JsonResponse({'userId': user_account.id, 'username': user_account.username, 'firstName': user_account.first_name, 'lastName': user_account.last_name, 'confidence': 100})


@csrf_exempt
def perform_sign_out(request):
    '''Perform the sign out based on facial recognition.'''
    face_found, user_id = parse_roaster_signing_requests(request)

    if not face_found:
        return HttpResponse('Error', status=MyResponseCodes.NO_FACE_FOUND)
    # Retrieve the location and user account objects
    location_id = 1  # TODO:clean
    location = Location.objects.get(pk=location_id)
    user_account = UserAccount.objects.get(pk=user_id)
    # Check if the user is on the active roster or if permission is denied
    if not is_on_active_roster(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.NOT_ON_ROASTER)

    if is_permission_denied(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.LOCATION_PERMISSION_DENIED)
    # Sign out the user at the specified location
    sign_out_at_location(user_account, location)
    return HttpResponse('OK', status=200)


@csrf_exempt
def perform_sign_out1(request, location_id, user_account_id):
    '''Perform sign out based on user accoutn id and location id.(alternative method )'''
    location = Location.objects.get(pk=location_id)
    user_account = UserAccount.objects.get(pk=user_account_id)
    # Check if the user is on the active roster or if permission is denied
    if not is_on_active_roster(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.NOT_ON_ROASTER)

    if is_permission_denied(user_account, location):
        return HttpResponse('Error', status=MyResponseCodes.LOCATION_PERMISSION_DENIED)
    # Sign out the user at the specified location
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
    '''Change the password of the user.'''
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
