import logging
import re
from time import sleep
from urllib.error import HTTPError

import requests
import requests_mock
from requests.sessions import HTTPAdapter
from requests_mock import create_response
from urllib3 import Retry

logger = logging.getLogger(__name__)


def raise_and_log_error(response, *args, **kwargs):
    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception(
            "Got response with status code {}: {}".format(
                response.status_code, response.text
            )
        )
        raise
    return response


class ImageMocker:
    service_path = "/v1/images"

    def get_response(self, request):
        json_data = {
            "id": "j5cVSqLer",
            "url": "https://cdn2.thecatapi.com/images/j5cVSqLer.jpg",
            "breeds": [
                {
                    "weight": {"imperial": "5 - 9", "metric": "2 - 4"},
                    "id": "munc",
                    "name": "Munchkin",
                    "vetstreet_url": "http://www.vetstreet.com/cats/munchkin",
                    "temperament": "Agile, Easy Going, Intelligent, Playful",
                    "origin": "United States",
                    "country_codes": "US",
                    "country_code": "US",
                    "description": "The Munchkin is an outgoing cat who enjoys being handled. She has lots of energy and is faster and more agile than she looks. The shortness of their legs does not seem to interfere with their running and leaping abilities.",  # noqa E501
                    "life_span": "10 - 15",
                    "indoor": 0,
                    "lap": 1,
                    "alt_names": "",
                    "adaptability": 5,
                    "affection_level": 5,
                    "child_friendly": 4,
                    "dog_friendly": 5,
                    "energy_level": 4,
                    "grooming": 2,
                    "health_issues": 3,
                    "intelligence": 5,
                    "shedding_level": 3,
                    "social_needs": 5,
                    "stranger_friendly": 5,
                    "vocalisation": 3,
                    "experimental": 0,
                    "hairless": 0,
                    "natural": 0,
                    "rare": 0,
                    "rex": 0,
                    "suppressed_tail": 0,
                    "short_legs": 1,
                    "wikipedia_url": "https://en.wikipedia.org/wiki/Munchkin_(cat)",
                    "hypoallergenic": 0,
                    "reference_image_id": "j5cVSqLer",
                }
            ],
            "width": 1600,
            "height": 1200,
        }

        return create_response(request, json=json_data, status_code=200)


class BreedMocker:
    service_path = "/v1/breeds"

    def get_response(self, request):
        json_data = [
            {
                "weight": {"imperial": "7 - 10", "metric": "3 - 5"},
                "id": "aege",
                "name": "Aegean",
                "vetstreet_url": "http://www.vetstreet.com/cats/aegean-cat",
                "temperament": "Affectionate, Social, Intelligent, Playful, Active",
                "origin": "Greece",
                "country_codes": "GR",
                "country_code": "GR",
                "description": "Native to the Greek islands known as the Cyclades in the Aegean Sea, these are natural cats, meaning they developed without humans getting involved in their breeding. As a breed, Aegean Cats are rare, although they are numerous on their home islands. They are generally friendly toward people and can be excellent cats for families with children.",  # noqa F401
                "life_span": "9 - 12",
                "indoor": 0,
                "alt_names": "",
                "adaptability": 5,
                "affection_level": 4,
                "child_friendly": 4,
                "dog_friendly": 4,
                "energy_level": 3,
                "grooming": 3,
                "health_issues": 1,
                "intelligence": 3,
                "shedding_level": 3,
                "social_needs": 4,
                "stranger_friendly": 4,
                "vocalisation": 3,
                "experimental": 0,
                "hairless": 0,
                "natural": 0,
                "rare": 0,
                "rex": 0,
                "suppressed_tail": 0,
                "short_legs": 0,
                "wikipedia_url": "https://en.wikipedia.org/wiki/Aegean_cat",
                "hypoallergenic": 0,
                "reference_image_id": "ozEvzdVM-",
                "image": {
                    "id": "ozEvzdVM-",
                    "width": 1200,
                    "height": 800,
                    "url": "https://cdn2.thecatapi.com/images/ozEvzdVM-.jpg",
                },
            }
        ]

        return create_response(request, json=json_data, status_code=200)


class CatAPIMatcher:
    def __init__(self):
        self.mockers = {}
        for m in (BreedMocker(), ImageMocker()):
            self.mockers[m.service_path] = m

    def __call__(self, request, *args, **kwargs):
        request_pattern = request.path
        for request_path, mock in self.mockers.items():
            if re.match(request_pattern, request_path):
                return self.mockers[request_pattern].get_response(request)
        raise Exception(f"Unknown mock request received: {request_pattern}")


class CatsAPIClient:
    def __init__(self, host="", api_key=""):
        self.host = host
        self.api_key = api_key
        self.use_mocks = self.host.startswith("mock://")

        session = requests.Session()
        session.hooks["response"] = [raise_and_log_error]

        if self.use_mocks:
            mock_adapter = requests_mock.Adapter()
            session.mount("mock://", mock_adapter)
            mock_adapter.add_matcher(CatAPIMatcher())
        else:
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 503],
                allowed_methods=["GET", "POST"],
                backoff_factor=2,
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount(self.host, adapter)

        self.session = session

    def get_breeds(self, page=0, limit=10):
        url = f"{self.host}/v1/breeds"
        params = {"page": page, "limit": limit}
        print(f"Fetching breeds: {url} - {params}")
        logger.info(f"Fetching breeds: {url} - {params}")
        response = self.session.request("GET", url=url, params=params)
        data = response.json()
        return data

    def get_images(self, image_ids):
        images = []
        for image_id in image_ids:
            url = f"{self.host}/v1/images/{image_id}"
            print(f"Fetching images: {url}")
            response = self.session.request("GET", url=url)
            data = response.json()
            images.append(data)
            sleep(1)

        return images


if __name__ == "__main__":
    host = "mock://api.thecatapi.com"
    api_key = ""
    api_client = CatsAPIClient(host=host, api_key=api_key)
    breeds = api_client.get_breeds(limit=1)
    print(breeds)
