from django.shortcuts import get_object_or_404, render

from django.http import HttpResponse
from .models import Location

def index(request):
    return HttpResponse("Hello, world. You're at the Identity index.")

def locations(request):
    locations: list(Location) = Location.objects.order_by('-name')
    return render(request, 'locations/index.html', {'locations': locations})

def location_details(request, location_id):
    location = get_object_or_404(Location, pk=location_id)
    return render(request, 'locations/details.html', {'location': location})

