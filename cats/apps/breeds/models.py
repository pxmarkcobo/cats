import logging

from django.db import models

logger = logging.getLogger(__name__)


class Image(models.Model):
    external_id = models.CharField(max_length=200, unique=True)
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    url = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.external_id}"


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
        old_reference_image_id = None
        if self.pk:
            old_reference_image_id = self.reference_image_id

        super().save(**kwargs)
        if old_reference_image_id != self.reference_image_id or (
            self.reference_image_id and not self.image
        ):
            if self.reference_image_id:
                try:
                    image = Image.objects.get(external_id=self.reference_image_id)
                except Image.DoesNotExist:
                    logger.warning(
                        f"Image with external ID {self.reference_image_id} not found!"
                    )
                    pass
                else:
                    self.image = image
            else:
                self.image = None
        return super().save(**kwargs)
