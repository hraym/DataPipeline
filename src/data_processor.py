import pandas as pd
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    @staticmethod
    def process_world_bank_data(data: List[Dict], indicator_code: str) -> Tuple[pd.DataFrame, str]:
        if not data:
            logger.warning(f"No data retrieved for indicator: {indicator_code}")
            return pd.DataFrame(), indicator_code

        df = pd.DataFrame(data)

        # Extract the indicator name from the first row
        indicator_name = indicator_code
        if 'indicator' in df.columns and len(df) > 0:
            indicator_value = df['indicator'].iloc[0]
            if isinstance(indicator_value, dict) and 'value' in indicator_value:
                indicator_name = indicator_value['value']
            elif isinstance(indicator_value, str):
                indicator_name = indicator_value

        if 'country' in df.columns:
            df['country_name'] = df['country'].apply(lambda x: x['value'] if isinstance(x, dict) else x)
        elif 'country_name' not in df.columns:
            logger.warning(f"No 'country' or 'country_name' column found for indicator: {indicator_code}")
            return pd.DataFrame(), indicator_name

        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['date'], format='%Y', errors='coerce')

        columns_to_drop = ['indicator', 'obs_status', 'decimal', 'unit', 'country']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
        df = df.rename(columns={'countryiso3code': 'country_code', 'date': 'year', 'value': indicator_code})

        # Set multi-index
        df = df.set_index(['country_name', 'country_code', 'year'])

        logger.info(f"Successfully processed data for indicator: {indicator_code}")
        return df, indicator_name