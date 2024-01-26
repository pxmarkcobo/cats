from django.contrib import admin

from cats.apps.breeds.models import Breed, Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("pk", "external_id", "url")


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ("pk", "external_id", "name")
    list_select_related = ("image",)
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "external_id",
                    "name",
                    "description",
                    "alt_names",
                    "country_code",
                    "vetstreet_url",
                    "wikipedia_url",
                    "reference_image_id",
                    "image",
                ),
            },
        ),
        (
            "Life Span",
            {
                "fields": (
                    "life_span_min",
                    "life_span_max",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Weight Information",
            {
                "fields": (
                    "weight_imperial_min",
                    "weight_imperial_max",
                    "weight_metric_min",
                    "weight_metric_max",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Temperament",
            {
                "fields": (
                    "temperament",
                    "adaptability",
                    "affection_level",
                    "child_friendly",
                    "dog_friendly",
                    "energy_level",
                    "grooming",
                    "health_issues",
                    "intelligence",
                    "shedding_level",
                    "social_needs",
                    "stranger_friendly",
                    "vocalisation",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Characteristics",
            {
                "fields": (
                    "indoor",
                    "experimental",
                    "hairless",
                    "natural",
                    "rare",
                    "rex",
                    "suppressed_tail",
                    "short_legs",
                    "hypoallergenic",
                ),
                "classes": ("collapse",),
            },
        ),
    )
