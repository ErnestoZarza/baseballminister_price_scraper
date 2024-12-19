from decimal import Decimal
import html
import json
import random
import re
import time
from statistics import mean

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from utils import ScrapeStatus, USER_AGENT_LIST


class BaseBallMinisterPriceScraper:
    def __init__(self, timeout: int = 3, retry: int = 3):
        self.timeout = timeout
        self.retry = retry
        self.invalid_response = 0
        self.no_search_msg = 'Leider wurde zu Deinem Suchbegriff nichts gefunden'
        self.base_url = 'https://www.baseballminister.de/search/?qs='

    @staticmethod
    def parse_price_vat(price_string: str) -> Decimal:
        # the scraped prices are missing the vat % so we need to add it to the final prices
        return (Decimal(price_string) * Decimal('1.19')).quantize(Decimal('0.01'))

    @classmethod
    def parse_response(cls, response: str, target_item: str, pattern: str) -> list[dict] | None:
        if response is None:
            print('Response was empty')
            return None

        parser = BeautifulSoup(response, 'html.parser')
        script_tags = parser.find_all(
            'script', {'type': 'text/javascript', 'data-eucid': 'google_analytics4'}
        )
        extracted_data = None

        try:
            # We can get multiple results for the same tag
            for script in script_tags:
                content_str = script.string or ''
                if target_item in content_str:
                    matched_data = re.search(pattern, content_str, re.DOTALL)
                    if matched_data:
                        # Decode HTML entities (german characters)
                        items_data = html.unescape(matched_data.group(1))
                        # Switching the case when whe have inches for the bats: (example 34")
                        items_data = items_data.replace('"', "")
                        # Replace keys and values single quotes from javascript keys and values
                        items_data = items_data.replace("'", '"')
                        items = json.loads(items_data)
                        extracted_data = [
                            {
                                'price': cls.parse_price_vat(item['price']),
                                'brand': item['item_brand'],
                            }
                            for item in items
                        ]
                    break

        except Exception as exception:
            print(f'There is a problem with the response formatting: {exception}')

        return extracted_data

    def _get_response_with_retry_strategy(self, url: str):
        # setting the cases when we want to perform a retry
        retry_strategy = Retry(
            allowed_methods=['HEAD', 'GET', 'OPTIONS'],
            status_forcelist=[500, 502, 503, 504],
            backoff_factor=1,
            total=self.retry,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http_request = requests.Session()
        http_request.mount('https://', adapter)
        http_request.mount('http://', adapter)
        # using random user agents to prevent any anti-scraper conditions
        user_agent = random.choice(USER_AGENT_LIST)
        header = {'User-Agent': user_agent}

        response = http_request.get(url, headers=header, timeout=60)
        response.raise_for_status()
        return response

    def is_valid_prices_response(
        self, response: str, target_item: str = "gtag('event', 'view_item_list'"
    ) -> bool:
        if not response:
            return False

        parser = BeautifulSoup(response, 'html.parser')
        script_tags = parser.find_all(
            'script', {'type': 'text/javascript', 'data-eucid': 'google_analytics4'}
        )
        # searching for the script that contains the unique identifier with prices
        contains_prices = any(target_item in (script.string or '') for script in script_tags)

        return contains_prices and not self.is_no_search_results(response)

    def is_no_search_results(self, response: str, no_search_class='alert alert-info') -> bool:
        paser = BeautifulSoup(response, 'html.parser')
        no_search_div = paser.find('div', {'class': no_search_class})
        if no_search_div:
            no_search_text = no_search_div.get_text(strip=True)
            return self.no_search_msg in no_search_text

        return False

    def custom_sleep(self, retries):
        sleep_time = random.randint(15, 60) if retries > 0 else self.timeout
        print(f'Sleeping for {sleep_time} seconds...')
        time.sleep(sleep_time)

    def get_response_with_retry_strategy(self, url: str) -> (list | None, ScrapeStatus):
        retries = 0
        response = None
        status = ScrapeStatus.OTHER_ERROR

        while retries < self.retry:
            try:
                # getting the response
                response = self._get_response_with_retry_strategy(url)

                # checking if we have prices
                if self.is_valid_prices_response(response.text):
                    return response, ScrapeStatus.VALID_PRICES

                # checking if we can identify the no search results
                if self.is_no_search_results(response.text):
                    return None, ScrapeStatus.NOT_FOUND

                print(f'Invalid price data: Sleeping for {self.timeout} seconds')
                self.custom_sleep(retries)

            # checking known possible requests errors
            except requests.exceptions.HTTPError as http_err:
                http_code = http_err.response.status_code
                status = (
                    ScrapeStatus.TOO_MANY_REQUESTS_ERROR if http_code == 429
                    else ScrapeStatus.REQUEST_ERROR
                )
                print(f'This HTTPError happened {http_code}: {http_err}')
                self.custom_sleep(retries)

            except requests.exceptions.RetryError as e:
                status = ScrapeStatus.SERVER_ERROR
                print(f'Retry Error: {e}')
                self.custom_sleep(retries)

            except requests.exceptions.RequestException as e:
                status = ScrapeStatus.REQUEST_ERROR
                print(f'This exception happened: {e}')
                self.custom_sleep(retries)

            except Exception as e:
                status = ScrapeStatus.OTHER_ERROR
                print(f'Unhandled exception: {e}')
                self.custom_sleep(retries)

            retries += 1

        return response, status

    def get_prices(self, category: str = 'softballschlaeger') -> (list | None, dict, ScrapeStatus):
        url = f'{self.base_url}{category}'
        print(f'Scraping data for {url}')

        response, response_status = self.get_response_with_retry_strategy(url)

        if response_status != ScrapeStatus.VALID_PRICES:
            return [], {}, response_status

        target_item = "gtag('event', 'view_item_list'"
        target_pattern = r"'items':\s*(\[.*?\])"

        response_data = self.parse_response(response.text, target_item, target_pattern)
        if response_data is None:
            return [], {}, ScrapeStatus.PARSING_ERROR

        prices = [data['price'] for data in response_data]
        prices_statistics = {
            'total_count': len(prices),
            'avg_price': mean(prices).quantize(Decimal('0.01')),
            'max_price': max(prices),
            'min_price': min(prices),
        }

        return response_data, prices_statistics, response_status
