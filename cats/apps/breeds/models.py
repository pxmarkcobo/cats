from django.db import models


class Image(models.Model):
    external_id = models.CharField(max_length=200, unique=True)
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    url = models.CharField(max_length=200, blank=True)


class Breed(models.Model):
    external_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    alt_names = models.CharField(max_length=200, blank=True)
    origin = models.CharField(max_length=200, blank=True)
    country_code = models.CharField(max_length=200, blank=True)
    vetstreet_url = models.CharField(max_length=200, blank=True)
    wikipedia_url = models.CharField(max_length=200, blank=True)

    # weight info
    weight_imperial_min = models.PositiveSmallIntegerField(null=True)
    weight_imperial_max = models.PositiveSmallIntegerField(null=True)
    weight_metric_min = models.PositiveSmallIntegerField(null=True)
    weight_metric_max = models.PositiveSmallIntegerField(null=True)

    # lifespan info
    life_span_min = models.PositiveSmallIntegerField(null=True)
    life_span_max = models.PositiveSmallIntegerField(null=True)

    # breed temperament
    temperament = models.CharField(max_length=200, blank=True)
    adaptability = models.PositiveSmallIntegerField(null=True)
    affection_level = models.PositiveSmallIntegerField(null=True)
    child_friendly = models.PositiveSmallIntegerField(null=True)
    dog_friendly = models.PositiveSmallIntegerField(null=True)
    energy_level = models.PositiveSmallIntegerField(null=True)
    grooming = models.PositiveSmallIntegerField(null=True)
    health_issues = models.PositiveSmallIntegerField(null=True)
    intelligence = models.PositiveSmallIntegerField(null=True)
    shedding_level = models.PositiveSmallIntegerField(null=True)
    social_needs = models.PositiveSmallIntegerField(null=True)
    stranger_friendly = models.PositiveSmallIntegerField(null=True)
    vocalisation = models.PositiveSmallIntegerField(null=True)

    indoor = models.BooleanField(null=True, blank=True)
    experimental = models.BooleanField(null=True, blank=True)
    hairless = models.BooleanField(null=True, blank=True)
    natural = models.BooleanField(null=True, blank=True)
    rare = models.BooleanField(null=True, blank=True)
    rex = models.BooleanField(null=True, blank=True)
    suppressed_tail = models.BooleanField(null=True, blank=True)
    short_legs = models.BooleanField(null=True, blank=True)
    hypoallergenic = models.BooleanField(null=True, blank=True)

    reference_image_id = models.CharField(max_length=200, blank=True)
    image = models.ForeignKey(
        Image, related_name="breeds", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.external_id} - {self.name}"

    def save(self, **kwargs):
        if self.reference_image_id and self.image is None:
            image = Image.objects.filter(external_id=self.reference_image_id)
            if image.exists():
                self.image = image.first()
        else:
            self.image = None
        return super().save(**kwargs)
