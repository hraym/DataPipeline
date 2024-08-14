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

    @staticmethod
    def preprocess_for_visualization(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        processed_data = {}
        for indicator, df in data.items():
            # Reset the index to convert MultiIndex to columns
            df_reset = df.reset_index()
            # Set 'year' as the index
            df_reset = df_reset.set_index('year')
            # Drop the 'country_code' column
            df_reset = df_reset.drop(columns=['country_code'])
            # Pivot the dataframe
            df_pivot = df_reset.pivot(columns='country_name', values=indicator)
            processed_data[indicator] = df_pivot
        return processed_data