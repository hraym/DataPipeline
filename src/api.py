import aiohttp
from typing import List, Dict
from .exceptions import WorldBankAPIError

class WorldBankAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_data(self, session: aiohttp.ClientSession, indicator: str, 
                         countries: List[str], start_year: int, end_year: int) -> List[Dict]:
        countries_str = ';'.join(countries)
        url = f"{self.base_url}/country/{countries_str}/indicator/{indicator}"
        params = {
            'format': 'json',
            'per_page': 10000,
            'date': f"{start_year}:{end_year}"
        }

        all_data = []
        page = 1

        while True:
            params['page'] = page
            try:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

                if not data or len(data) < 2 or not data[1]:
                    break

                all_data.extend(data[1])

                if len(data[1]) < params['per_page']:
                    break

                page += 1
            except aiohttp.ClientError as e:
                raise WorldBankAPIError(f"Error fetching data for {indicator}: {str(e)}")

        return all_data

