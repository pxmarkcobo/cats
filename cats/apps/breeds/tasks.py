import logging

from django.conf import settings

from cats.apps.breeds.models import Breed, Image
from cats.utils.client import CatsAPIClient
from config import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def download_breeds(self):
    client = CatsAPIClient(
        host=settings.CATS_API_HOST,
        api_key=settings.CATS_API_KEY,
    )

    breeds = []
    total_count = 0
    page = 0
    limit = settings.CATS_API_DATA_LIMIT
    while True:
        data = client.get_breeds(page=page, limit=limit)
        data_len = len(data)

        breeds.extend(data)
        total_count += data_len

        if len(data) < limit:
            break

        page += 1

    # Fetch image data on demand
    image_ids = {
        obj["reference_image_id"]
        for obj in breeds
        if obj.get("reference_image_id", None)
    }

    images = []
    if image_ids:
        existing_images = set(Image.objects.values_list("external_id", flat=True))
        image_ids = image_ids - existing_images
        images = client.get_images(image_ids)

    for image in images:
        obj, _ = Image.objects.get_or_create(
            external_id=image["id"],
            url=image["url"],
            width=image["width"],
            height=image["height"],
        )

    for breed in breeds:
        obj, _ = Breed.objects.get_or_create(external_id=breed["id"])

        obj.name = breed["name"]
        obj.description = breed["description"]
        obj.alt_names = breed.get("alt_names", "")
        obj.origin = breed.get("origin", "")
        obj.country_code = breed.get("country_code", "")
        obj.vetstreet_url = breed.get("vetstreet_url", "")
        obj.wikipedia_url = breed.get("wikipedia_url", "")

        # weight
        weight_imperial = (breed["weight"]["imperial"]).split(" - ")
        obj.weight_imperial_min = int(weight_imperial[0])
        obj.weight_imperial_max = int(weight_imperial[1])

        weight_metric = (breed["weight"]["metric"]).split(" - ")
        obj.weight_metric_min = int(weight_metric[0])
        obj.weight_metric_max = int(weight_metric[1])

        # lifespan
        life_span = (breed["life_span"]).split(" - ")
        obj.life_span_min = int(life_span[0])
        obj.life_span_max = int(life_span[1])

        # temperament
        obj.temperament = breed["temperament"]
        obj.adaptability = breed["adaptability"]
        obj.affection_level = breed["affection_level"]
        obj.child_friendly = breed["child_friendly"]
        obj.dog_friendly = breed["dog_friendly"]
        obj.energy_level = breed["energy_level"]
        obj.grooming = breed["grooming"]
        obj.health_issues = breed["health_issues"]
        obj.intelligence = breed["intelligence"]
        obj.shedding_level = breed["shedding_level"]
        obj.social_needs = breed["social_needs"]
        obj.stranger_friendly = breed["stranger_friendly"]
        obj.vocalisation = breed["vocalisation"]

        # characteristics
        obj.indoor = bool(breed["indoor"])
        obj.experimental = bool(breed["experimental"])
        obj.hairless = bool(breed["hairless"])
        obj.natural = bool(breed["natural"])
        obj.rare = bool(breed["rare"])
        obj.rex = bool(breed["rex"])
        obj.suppressed_tail = bool(breed["suppressed_tail"])
        obj.short_legs = bool(breed["short_legs"])
        obj.hypoallergenic = bool(breed["hypoallergenic"])

        # image
        obj.reference_image_id = breed.get("reference_image_id", "")
        obj.save()
