from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'home.html')

def test_endpoint(request):
    return HttpResponse("HTMX works!")