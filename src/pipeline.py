import pandas as pd
from typing import List, Dict, Tuple
import logging
from .api import WorldBankAPI
from .data_processor import DataProcessor
from .exceptions import WorldBankAPIError, DataProcessingError

logger = logging.getLogger(__name__)

class WorldBankDataPipeline:
    def __init__(self, api: WorldBankAPI, processor: DataProcessor):
        self.api = api
        self.processor = processor
        self.indicator_mapping = {}

    def process_indicator_data(self, indicator: str, raw_data: List[Dict]) -> pd.DataFrame:
        try:
            df, indicator_name = self.processor.process_world_bank_data(raw_data, indicator)
            self.indicator_mapping[indicator] = indicator_name
            logger.info(f"Successfully processed data for {indicator}")
            return df
        except DataProcessingError as e:
            logger.exception(f"Error processing data for {indicator}: {str(e)}")
            return pd.DataFrame()

    def fetch_all_indicators(self, indicators: List[str], countries: List[str], 
                             start_year: int, end_year: int) -> Dict[str, pd.DataFrame]:
        queries = [(indicator, countries, start_year, end_year) for indicator in indicators]
        raw_results = self.api.batch_fetch_data(queries)

        processed_results = {}
        for indicator, raw_data in raw_results.items():
            df = self.process_indicator_data(indicator, raw_data)
            if not df.empty:
                processed_results[indicator] = df

        return processed_results

def get_world_bank_data(indicator_codes: List[str], countries: List[str], 
                        start_year: int = 1960, end_year: int = None, max_workers: int = 10) -> Tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
    if end_year is None:
        end_year = pd.Timestamp.now().year

    api = WorldBankAPI('https://api.worldbank.org/v2', max_workers=max_workers)
    processor = DataProcessor()
    pipeline = WorldBankDataPipeline(api, processor)

    results = pipeline.fetch_all_indicators(indicator_codes, countries, start_year, end_year)
    return results, pipeline.indicator_mapping