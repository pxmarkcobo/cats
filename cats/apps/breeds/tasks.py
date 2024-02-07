import base64
import logging

import requests
from django.conf import settings
from django.core.files.base import ContentFile

from cats.apps.breeds.models import Breed, Image
from cats.utils.client import CatsAPIClient
from config import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def download_breeds():
    client = CatsAPIClient(
        host=settings.CATS_API_HOST,
        api_key=settings.CATS_API_KEY,
    )

    breeds = []
    page = 0
    limit = settings.CATS_API_DATA_LIMIT
    while True:
        data = client.get_breeds(page=page, limit=limit)
        breeds.extend(data)
        if len(data) < limit:
            break
        page += 1

    logger.info(f"Fetched total of {len(breeds)} breeds.")

    image_ids = {
        obj["reference_image_id"]
        for obj in breeds
        if obj.get("reference_image_id", None)
    }
    # Fetch image raw data on demand
    fetch_images(client, image_ids)

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
        image_id = breed.get("reference_image_id")
        if image_id:
            obj.reference_image_id = image_id
        obj.save()


def fetch_images(client, image_ids):
    if not image_ids:
        return

    existing_images = set(Image.objects.values_list("external_id", flat=True))
    missing_images = image_ids - existing_images
    logger.info(f"Missing image IDs: {missing_images}")

    if not missing_images:
        logger.info("No images to retrieve.")
        return

    for image_id in missing_images:
        image = client.get_image(image_id)
        obj = Image.objects.create(
            external_id=image["id"],
            url=image["url"],
            width=image["width"],
            height=image["height"],
        )
        url = image["url"]
        logger.info(f"Fetching raw image data: {url}")

        response = requests.get(url)
        if response.status_code == 200:
            filename = url.split("/")[-1]
            logger.info(f"Saving image raw data in file: {filename}")
            image_data = base64.b64decode(base64.b64encode(response.content).decode())
            obj.image = ContentFile(image_data, name=filename)
            obj.save()
        else:
            logger.info("Failed.")
