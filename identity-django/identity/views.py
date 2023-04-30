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
    """
    Custom view for updating a user's password.
    Inherits from Django's built-in PasswordChangeView and customizes the form class,
    template, and success URL. When a user successfully changes their password,
    they will be redirected to the locations page.

    Attributes:
        form_class: The form used to handle password changes, defaults to PasswordChangeForm.
        template_name: The template used to render the password change view, defaults to 'user-accounts/change-password.html'.
        success_url: The URL to redirect to upon successful password change, defaults to '/locations/'.
    """
    form_class = PasswordChangeForm
    template_name = 'user-accounts/change-password.html'
    success_url = reverse_lazy('/locations/')


def index(request):
    '''Index view, renders the home page of the website.'''
    return render(request, 'website/index.html')


def login_user(request):
    """
    Handles user login by verifying the user's credentials and logging them in if they are valid.

    If the request method is POST, the function retrieves the submitted username and password,
    then attempts to authenticate the user using Django's built-in authenticate function. If the
    user is authenticated, they are logged in, a success message is displayed, and they are
    redirected to the locations page. If the user is not authenticated, an error message is displayed,
    and the user is redirected back to the login page. If the request method is not POST, an error
    message is displayed, indicating an invalid username or password.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: A rendered template for the login page or a redirect to the locations page.
    """
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
    """
    Custom view for updating a user's profile.

    Inherits from Django's generic UpdateView and LoginRequiredMixin to ensure only
    authenticated users can access this view. Customizes the form class, template,
    and success URL. When a user successfully updates their profile, they will be
    redirected to the same page.

    Attributes:
        form_class: The form used to handle user profile updates, defaults to UserChangeForm.
        template_name: The template used to render the user edit view, defaults to 'user-accounts/edit-user-profile.html'.
        success_url: The URL to redirect to upon successful profile update, defaults to 'edit_user_profile'.

    Methods:
        get_object: Retrieves the current user's information to pre-populate the form.
    """
    form_class = UserChangeForm
    template_name = 'user-accounts/edit-user-profile.html'
    success_url = reverse_lazy('edit_user_profile')

    def get_object(self):
        return self.request.user


@login_required
def locations(request):
    """
    Display a list of all locations.

    This view is protected by the login_required decorator, ensuring that only
    authenticated users can access it. It queries the database for all Location
    objects, orders them by the 'name' attribute in descending order, and then renders
    the 'locations/index.html' template with the list of locations as context.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: A rendered template for the locations page.
    """
    locations: list(Location) = Location.objects.order_by('-name')
    return render(request, 'locations/index.html', {'locations': locations})


@login_required
@permission_required('identity.change_location', raise_exception=True)
def location_details(request, location_id):
    """
    Display detailed information about a specific location.

    This view is protected by the login_required decorator, ensuring that only
    authenticated users can access it. It retrieves the Location object based on the
    provided location_id and fetches the active sign-ins and roster logs for that
    location. The view then renders the 'locations/details.html' template with the
    location details, active sign-ins, and roster logs as context.

    Args:
        request: The HTTP request object.
        location_id: The primary key of the Location object to be displayed.

    Returns:
        HttpResponse: A rendered template for the location details page.
    """
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
    """
    Display detailed information about a specific location's roster log for a specific date.

    This view is protected by the login_required decorator, ensuring that only
    authenticated users can access it. It retrieves the Location object based on the
    provided location_id and fetches the roster logs for the specified location and date.
    The view then renders the 'locations/roster-details.html' template with the location
    details, the specified date, and the roster logs as context.

    Args:
        request: The HTTP request object.
        location_id: The primary key of the Location object to be displayed.
        location_sign_in_date: The date for which the roster logs should be displayed.

    Returns:
        HttpResponse: A rendered template for the location's roster details page.
    """
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
    """
    Display detailed information about a specific user account.

    This view is protected by the login_required decorator, ensuring that only
    authenticated users can access it. It retrieves the UserAccount object based on the
    provided user_account_id and renders the 'user-accounts/user-details-profile.html' 
    template with the user account details as context.

    Args:
        request: The HTTP request object.
        user_account_id: The primary key of the UserAccount object to be displayed.

    Returns:
        HttpResponse: A rendered template for the user account details page.
    """
    user_account = get_object_or_404(UserAccount, pk=user_account_id)
    return render(request, 'user-accounts/user-details-profile.html', {'user_account': user_account})


@login_required
def setup_facial_recognition(request):
    """
    Handles the setup of facial recognition for the logged in user.

    This view is protected by the login_required decorator, ensuring that only
    authenticated users can access it. It retrieves the UserAccount object for the
    logged-in user and checks if facial recognition is enabled for the user. If
    facial recognition is not enabled, the user is redirected to the
    'user-accounts/setup-facial-recognition-denied.html' template. Otherwise, the user
    is directed to the 'user-accounts/setup-facial-recognition.html' template to proceed
    with the setup process.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: A rendered template for the facial recognition setup page or
                      the facial recognition denied page.
    """
    user_account = get_object_or_404(UserAccount, pk=request.user.id)

    #TODO: Fix
    if not user_account.is_face_recognition_enabled:
        return render(request, 'user-accounts/setup-facial-recognition-denied.html', {'user_account_id': request.user.id})

    return render(request, 'user-accounts/setup-facial-recognition.html', {'user_account_id': request.user.id})


@login_required
def test(request):
    """
    Triggers the facial recognition training process and renders the test page.

    This view is protected by the login_required decorator, ensuring that only
    authenticated users can access it. The function initiates the facial
    recognition training process by calling the face_training() function. After
    the training process is complete, the 'user-accounts/test.html' template is
    rendered.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: A rendered template for the test page.
    """
    face_training()
    return render(request, 'user-accounts/test.html')


@login_required
def force_sign_out(_, roster_id):
    """
    Forces a sign out for a specific roster entry.

    This function retrieves the Roster object with the given roster_id, updates
    its sign_out_date to the current date and time, and saves the changes. After
    the sign-out process is complete, the function redirects the user to the
    location details page for the associated location.

    Args:
        _: The HTTP request object (ignored, hence the underscore).
        roster_id (int): The ID of the Roster object to force sign out.

    Returns:
        HttpResponseRedirect: A redirect to the location details page for the associated location.
    """
    roster: Roster = Roster.objects.get(
        id=roster_id)
    roster.sign_out_date = datetime.now()
    roster.save()
    return redirect(f'/locations/{roster.location.id}')


@login_required
@permission_required('identity.change_location', raise_exception=True)
def remove_permission(request, location_id, user_account_id):
    """
    Removes location permissions for a specific user account.

    This function checks if the logged-in user has permission to remove location
    permissions for other users. If the user has the required permission, it retrieves
    the LocationPermission object with the given location_id and user_account_id,
    and deletes it. After removing the permission, the function redirects the user
    to the location details page for the associated location. If the user does not
    have the required permission, it renders a permission denied page.

    Args:
        request (HttpRequest): The HTTP request object.
        location_id (int): The ID of the location for which the permission should be removed.
        user_account_id (int): The ID of the UserAccount object for which the permission should be removed.

    Returns:
        HttpResponseRedirect: A redirect to the location details page for the associated location.
        HttpResponse: Renders a permission denied page if the user does not have the required permission.
    """
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
    """
    Renders the sign-in page for a specific location.

    This function checks if the logged-in user has permission to sign in at the specified location.
    If the user has the required permission, it renders the sign-in page for the given location.
    If the user does not have the required permission, it raises a PermissionDenied exception.

    Args:
        request (HttpRequest): The HTTP request object.
        location_id (int): The ID of the Location object for which the user wants to sign in.

    Returns:
        HttpResponse: Renders the sign-in page for the specified location if the user has the required permission.
        PermissionDenied: Raises a PermissionDenied exception if the user does not have the required permission.
    """
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'user-accounts/sign-in-new.html', {'location': location})


@login_required
@permission_required('identity.activate_sign_off', raise_exception=True)
def sign_out(request, location_id):
    """
    Renders the sign-out page for a specific location.

    This function checks if the logged-in user has permission to sign out at the specified location.
    If the user has the required permission, it renders the sign-out page for the given location.
    If the user does not have the required permission, it raises a PermissionDenied exception.

    Args:
        request (HttpRequest): The HTTP request object.
        location_id (int): The ID of the Location object for which the user wants to sign out.

    Returns:
        HttpResponse: Renders the sign-out page for the specified location if the user has the required permission.
        PermissionDenied: Raises a PermissionDenied exception if the user does not have the required permission.
    """
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'user-accounts/sign-out.html', {'location': location})


@csrf_exempt
@permission_required('identity.activate_sign_in', raise_exception=True)
def perform_sign_in(request):
    """
    Perform the sign-in based on facial recognition.

    This function processes a facial recognition request to sign in a user at a specific location.
    It first checks if a face is detected and if the user is recognized. If not, it returns an error response.
    Next, it checks if the user is already on the active roster or if the user's permission is denied for the location.
    If the user passes all these checks, they are signed in at the specified location.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Returns an appropriate HTTP response based on the sign-in process outcome.
    """
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
    """
    Perform sign-in based on user account ID and location ID (alternative method).

    This function processes a sign-in request for a user at a specific location
    using user account ID and location ID as inputs. It first checks if the user
    is already on the active roster or if the user's permission is denied for the
    location. If the user passes these checks, they are signed in at the specified location.

    Args:
        request (HttpRequest): The HTTP request object.
        location_id (int): The ID of the location where the user wants to sign in.
        user_account_id (int): The ID of the user account to be signed in.

    Returns:
        HttpResponse: Returns an appropriate HTTP response based on the sign-in process outcome.
    """
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
    """
    Identify the user from their face and return their information as a JSON response.

    This function processes an HTTP request containing an image, identifies the user
    in the image using facial recognition, and returns their account information
    in a JSON response if the face is found. If no face is found, the response will
    indicate the failure by setting the 'userId' field to 0.

    Args:
        request (HttpRequest): The HTTP request object containing an image.

    Returns:
        JsonResponse: A JSON response containing the identified user's information, or
                      a response indicating that no face was found.
    """
    face_found, user_id = parse_roaster_signing_requests(request)

    if not face_found:
        return JsonResponse({'userId': 0})
    # Retrieve the user account object
    user_account = UserAccount.objects.get(pk=user_id)
    # Return the user's information in a JSON response
    return JsonResponse({'userId': user_account.id, 'username': user_account.username, 'firstName': user_account.first_name, 'lastName': user_account.last_name, 'confidence': 100})


@csrf_exempt
def perform_sign_out(request):
    """
    Perform the sign out based on facial recognition.

    This function processes an HTTP request containing an image, identifies the user
    in the image using facial recognition, and signs them out of a specified location
    if their face is found and they are on the active roster. If no face is found or
    the user is not on the active roster, an error response will be returned.

    Args:
        request (HttpRequest): The HTTP request object containing an image.

    Returns:
        HttpResponse: A response object indicating the success or failure of the sign-out process.
    """
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
    """
    Perform sign out based on user account id and location id (alternative method).

    This function signs out a user at a specified location using the user account id and
    location id provided. If the user is not on the active roster or if permission is denied,
    an error response will be returned.

    Args:
        request (HttpRequest): The HTTP request object.
        location_id (int): The id of the location to sign out from.
        user_account_id (int): The id of the user account to sign out.

    Returns:
        HttpResponse: A response object indicating the success or failure of the sign-out process.
    """
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
    """
    Receives a base64 encoded image for a user, detects a face, and saves the face to the system (folder on disk).

    This function processes a base64 encoded image received from the client, detects a face in the image,
    and saves the face to the system (folder on disk). If a face is found and it is the 30th image, the
    facial recognition training process will be triggered. If a face is found, an 'OK' response will be
    returned, otherwise an 'Error' response will be returned.

    Args:
        request (HttpRequest): The HTTP request object containing the base64 encoded image, user-account-id, and image-number.

    Returns:
        HttpResponse: A response object indicating the success or failure of the facial data upload process.
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
    """
    Change the password of the user.

    This function allows the user to change their password. It handles both GET and POST requests.
    If the request method is POST, it validates the submitted password change form, updates the user's password,
    and maintains the user's session. Upon successful password change, the user is redirected to the home page.
    If the request method is GET, it renders the password change form for the user to fill out.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A response object rendering the password change form or redirecting the user to the home page.
    """
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
