from django.urls import path

from cats.apps.breeds.views import BreedsListView

app_name = "breeds"
urlpatterns = [
    path("", BreedsListView.as_view(), name="list"),
]
