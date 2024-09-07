import requests
import time
import logging
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from .exceptions import WorldBankAPIError

logger = logging.getLogger(__name__)

class WorldBankAPI:
    def __init__(self, base_url: str, max_workers: int = 32, max_retries: int = 3, retry_backoff_factor: float = 0.1):
        self.base_url = base_url
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(total=self.max_retries, 
                      backoff_factor=self.retry_backoff_factor, 
                      status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({'User-Agent': 'WorldBankDataPipeline/1.0'})
        return session

    def test_connection(self) -> bool:
        """Test the connection to the World Bank API."""
        try:
            response = self.session.get(f"{self.base_url}/sources")
            response.raise_for_status()
            logger.info("Successfully connected to the World Bank API")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to connect to the World Bank API: {str(e)}")
            return False

    def fetch_indicator_data(self, indicator_code: str, country: str, start_year: int, end_year: int) -> List[Dict]:
        url = f"{self.base_url}/country/{country}/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'per_page': 3000,
            'date': f"{start_year}:{end_year}"
        }
    
        all_data = []
        page = 1
        retries = 0
    
        while retries < self.max_retries:
            try:
                params['page'] = page
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
    
                logger.debug(f"API Response for {indicator_code}, page {page}: {data}")
    
                if not isinstance(data, list) or len(data) < 2:
                    logger.warning(f"Invalid response format for indicator: {indicator_code}")
                    break
    
                metadata, page_data = data
                if not isinstance(page_data, list) or not page_data:
                    break
    
                all_data.extend(page_data)
                logger.info(f"Fetched {len(page_data)} records for {indicator_code}, page {page}")
    
                if page >= metadata.get('pages', 0):
                    break
    
                page += 1
                retries = 0  # Reset retries on successful request
    
            except (ConnectionError, Timeout) as e:
                logger.warning(f"Network error fetching data for {indicator_code}: {str(e)}. Retrying...")
                retries += 1
                time.sleep(2 ** retries)  # Exponential backoff
            except HTTPError as e:
                if e.response.status_code == 429:  # Too Many Requests
                    logger.warning("Rate limit exceeded. Waiting before retry...")
                    time.sleep(60)
                    retries += 1
                else:
                    logger.error(f"HTTP error fetching data for {indicator_code}: {str(e)}")
                    raise WorldBankAPIError(f"HTTP error fetching data for {indicator_code}: {str(e)}")
            except RequestException as e:
                logger.error(f"Error fetching data for {indicator_code}: {str(e)}")
                raise WorldBankAPIError(f"Error fetching data for {indicator_code}: {str(e)}")
    
        if retries == self.max_retries:
            logger.error(f"Max retries reached for indicator: {indicator_code}")
            raise WorldBankAPIError(f"Max retries reached for indicator: {indicator_code}")
    
        logger.info(f"Fetched {len(all_data)} records for indicator {indicator_code} and country {country}")
        return all_data
    
    def fetch_all_data(self, queries: List[Tuple[str, List[str], int, int]]) -> Dict[str, List[Dict]]:
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_query = {executor.submit(self.fetch_indicator_data, indicator_code, country, start_year, end_year): (indicator_code, country)
                               for indicator_code, countries, start_year, end_year in queries
                               for country in countries}
            
            for future in as_completed(future_to_query):
                indicator_code, country = future_to_query[future]
                try:
                    data = future.result()
                    if indicator_code not in results:
                        results[indicator_code] = []
                    results[indicator_code].extend(data)
                except Exception as e:
                    logger.error(f"Error fetching data for indicator {indicator_code} and country {country}: {str(e)}")
        
        return results

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    api = WorldBankAPI('https://api.worldbank.org/v2')
    
    # Test the API with a sample query
    indicators = ["NY.GDP.MKTP.CD", "SP.POP.TOTL"]
    countries = ["USA", "CHN", "JPN"]
    start_year = 1990
    end_year = 2023
    
    try:
        queries = [(indicator, countries, start_year, end_year) for indicator in indicators]
        results = api.batch_fetch_data(queries)
        for indicator, data in results.items():
            print(f"Fetched {len(data)} records for {indicator}")
            if data:
                print("Sample data:", data[0])
    except WorldBankAPIError as e:
        print(f"Error: {e}")