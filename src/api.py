import requests
import time
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from .exceptions import WorldBankAPIError
import logging

logger = logging.getLogger(__name__)

class WorldBankAPI:
    def __init__(self, base_url: str, max_workers: int = 10):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'WorldBankDataPipeline/1.0'})
        self.max_workers = max_workers

    def fetch_data(self, indicator: str, countries: List[str], start_year: int, end_year: int) -> List[Dict]:
        if start_year > end_year:
            raise WorldBankAPIError(f"Invalid year range: start_year ({start_year}) is greater than end_year ({end_year})")
        countries_str = ';'.join(countries)
        url = f"{self.base_url}/country/{countries_str}/indicator/{indicator}"
        params = {
            'format': 'json',
            'per_page': 1000,
            'date': f"{start_year}:{end_year}"
        }

        all_data = []
        page = 1

        while True:
            params['page'] = page
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if not data or len(data) < 2:
                    raise WorldBankAPIError(f"Invalid or empty response for indicator: {indicator}")

                metadata, page_data = data
                if not page_data:
                    break

                all_data.extend(page_data)

                if page >= metadata['pages']:
                    break

                page += 1
                
                rate_limit_remaining = int(response.headers.get('X-Rate-Limit-Remaining', '100'))
                logger.info(f"Fetched page {page} for indicator {indicator}. Rate limit remaining: {rate_limit_remaining}")

                if rate_limit_remaining <= 1:
                    logger.warning("Rate limit nearly reached. Pausing for 1 second.")
                    time.sleep(1)

            except requests.RequestException as e:
                logger.error(f"Error fetching data for {indicator}: {str(e)}")
                raise WorldBankAPIError(f"Error fetching data for {indicator}: {str(e)}")

        if not all_data:
            logger.warning(f"No data found for indicator: {indicator}")
            raise WorldBankAPIError(f"No data found for indicator: {indicator}")

        return all_data

    def batch_fetch_data(self, queries: List[Tuple[str, List[str], int, int]]) -> Dict[str, List[Dict]]:
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_indicator = {
                executor.submit(self.fetch_data, indicator, countries, start_year, end_year): indicator
                for indicator, countries, start_year, end_year in queries
            }

            for future in as_completed(future_to_indicator):
                indicator = future_to_indicator[future]
                try:
                    results[indicator] = future.result()
                except WorldBankAPIError as e:
                    logger.error(f"Error fetching data for {indicator}: {str(e)}")
                    results[indicator] = []

        return results

    def __del__(self):
        self.session.close()