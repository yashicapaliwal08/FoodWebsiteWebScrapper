import logging
import gzip
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from utils import requests_retry_session

class GrabFoodScraper: #class to extract data from API
    def __init__(self):
        self.api_url = "https://portal.grab.com/foodweb/v2/search" #api url
        self.headers = { #headers
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        }
        self.payload_template = { # payload template
            "countryCode": "SG",
            "keyword": "",
            "latlng": "1.396364,103.747462",
            "offset": 64,
            "pageSize": 32
        }
        logging.basicConfig(level=logging.INFO)
        self.session = requests_retry_session() #sets up a session with retry mechanism

    def get_restaurant_list(self):
        restaurant_list = []
        offset = 64
        page_size = self.payload_template["pageSize"]

        while True:
            try:
                response = self._make_request_with_backoff(offset, page_size) #fetches the list of restaurants by making paginated requests to the API
                logging.info(f"Request URL: {response.url}")
                logging.info(f"Response Status Code: {response.status_code}")

                if response.status_code != 200:
                    logging.error("Failed to fetch data from API")
                    break

                data = response.json()
                logging.info(f"Number of records in current response: {len(data['searchResult']['searchMerchants'])}") #length of response at that time

                if 'searchResult' in data and data['searchResult']['searchMerchants']:
                    restaurant_list.extend(data['searchResult']['searchMerchants'])
                else:
                    logging.warning("No restaurant data found")
                    break

                if len(data['searchResult']['searchMerchants']) < page_size:
                    break

                offset += page_size
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                break

        return restaurant_list

    def _make_request_with_backoff(self, offset, page_size, max_retries=5, initial_delay=1):
        delay = initial_delay
        for attempt in range(max_retries):
            try: #makes a request to the API with exponential backoff in case of failures
                payload = self.payload_template.copy()
                payload["offset"] = offset
                payload["pageSize"] = page_size

                response = self.session.post(self.api_url, headers=self.headers, json=payload)
                if response.status_code in [500, 502, 503, 504]:
                    logging.warning(f"Server error ({response.status_code}). Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    return response
            except requests.exceptions.RequestException as e: #if request fails after max retries
                logging.error(f"Request failed on attempt {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
        raise requests.exceptions.RequestException(f"Failed to complete request after {max_retries} attempts")

    def parse_restaurant_details(self, restaurant):
        try:
            details = {
                "restaurant_name": restaurant.get("address", {}).get("name"),
                "restaurant_cuisine": restaurant.get("merchantBrief", {}).get("cuisine"),
                "restaurant_rating": restaurant.get("merchantBrief", {}).get("rating"),
                "estimated_delivery_time": restaurant.get("estimatedDeliveryTime"),
                "restaurant_distance": restaurant.get("merchantBrief", {}).get("distanceInKm"),
                "promotional_offers": restaurant.get("merchantBrief", {}).get("promo"),
                "restaurant_notice": restaurant.get("merchantStatusInfo", {}).get("status"),
                "image_link": restaurant.get("merchantBrief", {}).get("photoHref"),
                "is_promo_available": bool(restaurant.get("merchantBrief", {}).get("promo")),
                "price": restaurant.get("estimatedDeliveryFee", {}).get("priceDisplay"),
                "restaurant_id": restaurant.get("id"),
                "latitude": restaurant.get("latlng", {}).get("latitude"),
                "longitude": restaurant.get("latlng", {}).get("longitude"),
            } #parses the details of a restaurant from the provided data
            return details
        except Exception as e:
            logging.error(f"Error parsing restaurant details: {e}")
            return None

    def scrape(self):
        try:
            restaurant_list = self.get_restaurant_list()
            if not restaurant_list: #if restaurant list is empty
                logging.warning("No restaurants found")
                return

            with ThreadPoolExecutor(max_workers=10) as executor: #applied multithreading
                futures = [executor.submit(self.parse_restaurant_details, restaurant) for restaurant in restaurant_list]
                for future in futures:
                    details = future.result()
                    if details:
                        self._save_to_ndjson(details)
        except Exception as e:
            logging.error(f"Error scraping data: {e}")

    def _save_to_ndjson(self, restaurant_details):
        with gzip.open('grab_food_data.ndjson.gz', 'at', encoding='utf-8') as output_file: #saves restaurant details to an NDJSON file with gzip compression
            output_file.write(json.dumps(restaurant_details) + '\n') #parsed restaurant details.
