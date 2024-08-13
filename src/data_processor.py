import pandas as pd
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    @staticmethod
    def process_world_bank_data(data: List[Dict], indicator: str) -> pd.DataFrame:
        if not data:
            logger.warning(f"No data retrieved for indicator: {indicator}")
            return pd.DataFrame()

        df = pd.DataFrame(data)

        df['country_name'] = df['country'].apply(lambda x: x['value'] if isinstance(x, dict) else x)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], format='%Y')

        df = df.drop(columns=['indicator', 'obs_status', 'decimal', 'country', 'unit'])
        df = df.rename(columns={'countryiso3code': 'country_code', 'date': 'year', 'value': indicator})

        return df.set_index(['country_name', 'country_code', 'year']).sort_index()