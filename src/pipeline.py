import asyncio
import aiohttp
import pandas as pd
from typing import List, Dict
import logging
from .api import WorldBankAPI
from .data_processor import DataProcessor
from .exceptions import WorldBankAPIError, DataProcessingError

logger = logging.getLogger(__name__)

class WorldBankDataPipeline:
    def __init__(self, api: WorldBankAPI, processor: DataProcessor):
        self.api = api
        self.processor = processor

    async def fetch_and_process_indicator(self, session: aiohttp.ClientSession, 
                                          indicator: str, 
                                          countries: List[str], 
                                          start_year: int, end_year: int) -> pd.DataFrame:
        try:
            raw_data = await self.api.fetch_data(session, indicator, countries, start_year, end_year)
            df = self.processor.process_world_bank_data(raw_data, indicator)
            logger.info(f"Successfully retrieved and processed data for {indicator}")
            return df
        except (WorldBankAPIError, DataProcessingError) as e:
            logger.exception(f"Error processing data for {indicator}: {str(e)}")
            return pd.DataFrame()

    async def fetch_all_indicators(self, indicators: List[str], 
                                   countries: List[str], start_year: int, end_year: int) -> Dict[str, pd.DataFrame]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_and_process_indicator(session, indicator, countries, start_year, end_year) 
                     for indicator in indicators]
            results = await asyncio.gather(*tasks)

        return {indicator: df for indicator, df in zip(indicators, results)}

async def get_world_bank_data(indicator_codes: List[str], countries: List[str], 
                              start_year: int = 1960, end_year: int = None) -> Dict[str, pd.DataFrame]:
    if end_year is None:
        end_year = pd.Timestamp.now().year

    api = WorldBankAPI('http://api.worldbank.org/v2')
    processor = DataProcessor()
    pipeline = WorldBankDataPipeline(api, processor)

    results = await pipeline.fetch_all_indicators(indicator_codes, countries, start_year, end_year)
    return results