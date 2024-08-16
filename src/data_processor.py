import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    @staticmethod
    def process_world_bank_data(data: List[Dict], indicator_code: str) -> Tuple[pd.DataFrame, str]:
        if not data:
            logger.warning(f"No data retrieved for indicator: {indicator_code}")
            return pd.DataFrame(columns=['country_name', 'country_code', 'year', indicator_code]), indicator_code

        df = pd.DataFrame(data)

        # Extract the indicator name
        indicator_name = indicator_code
        if 'indicator' in df.columns and len(df) > 0:
            indicator_value = df['indicator'].iloc[0]
            if isinstance(indicator_value, dict) and 'value' in indicator_value:
                indicator_name = indicator_value['value']
            elif isinstance(indicator_value, str):
                indicator_name = indicator_value

        # Process country information
        if 'country' in df.columns:
            df['country_name'] = df['country'].apply(lambda x: x['value'] if isinstance(x, dict) and 'value' in x else str(x))
            df['country_code'] = df['countryiso3code']
        else:
            logger.warning(f"No 'country' column found for indicator: {indicator_code}")
            return pd.DataFrame(columns=['country_name', 'country_code', 'year', indicator_name]), indicator_name

        # Process date and value
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['year'] = pd.to_datetime(df['date'], format='%Y', errors='coerce').dt.year

        # Select and rename columns
        columns_to_keep = ['country_name', 'country_code', 'year', 'value']
        df = df[columns_to_keep].rename(columns={'value': indicator_name})

        # Handle missing values
        df = df.dropna(subset=['country_name', 'country_code', 'year'])

        # Set index
        df = df.set_index(['country_name', 'country_code', 'year'])

        # Ensure numeric values are float64
        df[indicator_name] = df[indicator_name].astype('float64')

        logger.info(f"Successfully processed data for indicator: {indicator_code}")
        return df, indicator_name