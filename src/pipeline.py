import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime
from .api import WorldBankAPI
from .data_processor import DataProcessor
from .exceptions import WorldBankAPIError, DataProcessingError
from .database import MongoDBHandler

logger = logging.getLogger(__name__)

def get_world_bank_data(
    indicator_codes: List[str], 
    countries: List[str], 
    start_year: int = 1960, 
    end_year: Optional[int] = None, 
    max_workers: int = 32
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
    if end_year is None:
        end_year = datetime.now().year

    api = WorldBankAPI('https://api.worldbank.org/v2', max_workers=max_workers, max_retries=3, retry_backoff_factor=0.1)
    processor = DataProcessor()
    db_handler = MongoDBHandler()

    try:
        pipeline = WorldBankDataPipeline(api, processor, db_handler)

        # Fetch and store new data
        logger.info("Fetching and storing new data...")
        results = pipeline.fetch_all_indicators(indicator_codes, countries, start_year, end_year)

        # Retrieve all data from the database
        logger.info("Retrieving all data from the database...")
        data = pipeline.get_all_data(indicator_codes, countries, start_year, end_year)

        return data, pipeline.indicator_mapping
    except Exception as e:
        logger.error(f"An error occurred in the World Bank data pipeline: {str(e)}")
        raise
    finally:
        db_handler.close_connection()
        logger.info("World Bank data pipeline completed.")

class WorldBankDataPipeline:
    def __init__(self, api: WorldBankAPI, processor: DataProcessor, db_handler: MongoDBHandler):
        self.api = api
        self.processor = processor
        self.db_handler = db_handler
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
        results = {}
        current_year = datetime.now().year
        api_queries = []
    
        for indicator_code in indicators:
            logger.info(f"Processing indicator: {indicator_code}")
            db_data = self.db_handler.get_indicator_data(indicator_code, countries, start_year, end_year)
            
            if not db_data:
                logger.info(f"No data found in database for {indicator_code}. Will fetch from API.")
                api_start_year = start_year
                api_end_year = min(end_year, current_year)
                api_queries.append((indicator_code, countries, api_start_year, api_end_year))
            else:
                logger.info(f"Found {len(db_data)} records in database for {indicator_code}")
                latest_year = max(item['year'] for item in db_data)
                api_start_year = min(latest_year + 1, current_year)
                api_end_year = min(end_year, current_year)
                
                if api_start_year <= api_end_year:
                    logger.info(f"Updating {indicator_code} from {api_start_year} to {api_end_year}")
                    api_queries.append((indicator_code, countries, api_start_year, api_end_year))
                
                # Store the database data
                db_df = pd.DataFrame(db_data)
                db_df.set_index(['country_name', 'country_code', 'year'], inplace=True)
                results[indicator_code] = db_df
    
        # Fetch data from API for all queries
        if api_queries:
            logger.info(f"Fetching data for {len(api_queries)} indicators from API")
            api_results = self.api.fetch_all_data(api_queries)
    
            for indicator_code, api_data in api_results.items():
                if api_data:
                    processed_data, indicator_name = self.processor.process_world_bank_data(api_data, indicator_code)
                    if not processed_data.empty:
                        self.db_handler.insert_or_update_indicator_data(indicator_code, indicator_name, processed_data.reset_index().to_dict('records'))
                        logger.info(f"Successfully updated data for {indicator_code}")
                        
                        if indicator_code in results:
                            results[indicator_code] = pd.concat([results[indicator_code], processed_data])
                        else:
                            results[indicator_code] = processed_data
                        
                        self.indicator_mapping[indicator_code] = indicator_name
                    else:
                        logger.warning(f"No new data processed for {indicator_code}")
                else:
                    logger.info(f"No new data available from API for {indicator_code}")
    
        return results
    
    def get_all_data(self, indicators: List[str], countries: List[str], 
                     start_year: int, end_year: int) -> Dict[str, pd.DataFrame]:
        results = {}
        for indicator_code in indicators:  # Changed from 'indicator' to 'indicator_code'
            try:
                data = self.db_handler.get_indicator_data(indicator_code, countries, start_year, end_year)
                df = pd.DataFrame(data)
                if not df.empty:
                    df = df.set_index(['country_name', 'country_code', 'year'])
                    results[indicator_code] = df
                    logger.info(f"Retrieved data for {indicator_code}: {len(df)} records")
                else:
                    logger.warning(f"No data retrieved for {indicator_code}")
            except Exception as e:
                logger.error(f"Error retrieving data for {indicator_code}: {str(e)}")
        return results
