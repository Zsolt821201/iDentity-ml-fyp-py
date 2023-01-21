from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse
from .models import Location

def index(request):
    return render(request, 'website/index.html')

def setup_facial_recognition(request):
    return render(request, 'user-accounts/setup-facial-recognition.html')

def locations(request):
    locations: list(Location) = Location.objects.order_by('-name')
    return render(request, 'locations/index.html', {'locations': locations})

def location_details(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'locations/details.html', {'location': location})

