# from django.shortcuts import render
from django.views.generic import ListView

from cats.apps.breeds.models import Breed

# Create your views here.


class BreedsListView(ListView):
    model = Breed
    template_name = "breeds/list.html"
    context_object_name = "breeds"
