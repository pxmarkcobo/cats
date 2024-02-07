from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView

from cats.apps.breeds.models import Breed, Image


class BreedsListView(ListView):
    model = Breed
    template_name = "breeds/list.html"
    context_object_name = "breeds"
    ordering = "pk"


class BreedDetailView(DetailView):
    model = Breed
    template_name = "breeds/partials/detail.html"
    context_object_name = "breed"


class HomeView(View):
    template_name = "pages/home.html"

    def get(self, request, *args, **kwargs):
        images = [obj.image.url for obj in Image.objects.all()]
        response = render(
            request,
            template_name=self.template_name,
            context={"images": images},
        )
        return response
