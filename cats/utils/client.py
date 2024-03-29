import logging
import re
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


class ImagesMocker:
    service_path = "/v1/images/search"

    def get_response(self, request):
        json_data = [
            {
                "id": "j5cVSqLer",
                "url": "https://cdn2.thecatapi.com/images/j5cVSqLer.jpg",
                "width": 1600,
                "height": 1200,
            }
        ]
        return create_response(request, json=json_data, status_code=200)


class SingleImageMocker:
    service_path = "/v1/images/(?P<id>.*)"

    def get_response(self, request):
        match = re.match(self.service_path, request.path)
        external_id = match.group("id")

        json_data = {
            "id": external_id,
            "url": "https://cdn2.thecatapi.com/images/j5cVSqLer.jpg",
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
            }
        ]

        return create_response(request, json=json_data, status_code=200)


class CatAPIMatcher:
    def __init__(self):
        self.mockers = {}
        for m in (BreedMocker(), ImagesMocker(), SingleImageMocker()):
            self.mockers[m.service_path] = m

    def __call__(self, request, *args, **kwargs):
        request_pattern = request.path
        for mock_path, mock in self.mockers.items():
            if re.match(mock_path, request_pattern):
                return self.mockers[mock_path].get_response(request)
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

        logger.info(f"Cats API: fetching breeds: {url} - {params}")
        response = self.session.request("GET", url=url, params=params)
        data = response.json()
        return data

    def get_image(self, image_id):
        url = f"{self.host}/v1/images/{image_id}"

        logger.info(f"Cats API: fetching image data: {url}")
        response = self.session.request("GET", url=url)
        data = response.json()
        return data

    def search_images(self, page=0, limit=10):
        url = f"{self.host}/v1/images/search"
        params = {"page": page, "limit": limit, "has_breeds": 1, "order": "DESC"}

        logger.info(f"Cats API: fetching random images: {url} - {params}")
        response = self.session.request("GET", url=url, params=params)
        data = response.json()
        return data


if __name__ == "__main__":
    host = "mock://api.thecatapi.com"
    api_key = ""
    api_client = CatsAPIClient(host=host, api_key=api_key)
    breeds = api_client.get_breeds(limit=1)
    print(breeds)
