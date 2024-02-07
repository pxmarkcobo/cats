from django.urls import path

from cats.apps.breeds.views import BreedDetailView, BreedsListView

app_name = "breeds"
urlpatterns = [
    path("", BreedsListView.as_view(), name="list"),
    path("<int:pk>", BreedDetailView.as_view(), name="detail"),
]
