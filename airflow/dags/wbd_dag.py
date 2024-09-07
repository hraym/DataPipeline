import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parents[3]  # Adjust the number if needed
sys.path.append(str(project_root))

from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException
from datetime import datetime, timedelta
from pendulum import duration
from DataPipeline.src.pipeline import get_world_bank_data
from DataPipeline.src.database import MongoDBHandler
from DataPipeline.src.dashboard import create_dashboard, run_dashboard
from DataPipeline.src.indicators_config import get_all_indicator_codes
from DataPipeline.src.exceptions import WorldBankAPIError, DataProcessingError
from DataPipeline.src.api import WorldBankAPI
import logging
import pandas as pd

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': duration(minutes=5),
}

@dag(
    'world_bank_data_pipeline',
    default_args=default_args,
    description='Monthly DAG to update World Bank data and refresh dashboard',
    schedule_interval='@monthly',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['world_bank', 'data_pipeline'],
)
def world_bank_data_pipeline():

    @task()
    def check_missing_data():
        try:
            db_handler = MongoDBHandler()
            api = WorldBankAPI('https://api.worldbank.org/v2', max_workers=10)
            indicator_codes = get_all_indicator_codes()
            
            missing_data = {}
            current_year = datetime.now().year - 1  # We use previous year as the latest available data

            for indicator in indicator_codes:
                # Get the latest data from the database
                latest_data = db_handler.get_indicator_data(indicator)
                
                if not latest_data:
                    # If no data exists, fetch all available data
                    missing_data[indicator] = {
                        'countries': ['all'],
                        'start_year': 1960,
                        'end_year': current_year
                    }
                else:
                    # Find missing countries and years
                    db_countries = set(item['country_code'] for item in latest_data)
                    db_years = set(item['year'] for item in latest_data)
                    
                    # Fetch a small amount of recent data to get the list of available countries for this indicator
                    recent_data = api.fetch_indicator_data(indicator, 'all', current_year - 1, current_year)
                    available_countries = set(item['country']['id'] for item in recent_data if 'country' in item)
                    
                    missing_countries = list(available_countries - db_countries)
                    
                    # Find the earliest and latest years in the database
                    min_year = min(db_years)
                    max_year = max(db_years)
                    
                    if missing_countries or min_year > 1960 or max_year < current_year:
                        missing_data[indicator] = {
                            'countries': missing_countries if missing_countries else ['all'],
                            'start_year': min(1960, min_year),
                            'end_year': current_year
                        }
            
            logger.info(f"Missing data check completed. {len(missing_data)} indicators need updating.")
            return missing_data
        
        except WorldBankAPIError as e:
            logger.error(f"Error fetching data from World Bank API: {str(e)}")
            raise AirflowException(f"World Bank API Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error checking for missing data: {str(e)}")
            raise AirflowException(f"Missing Data Check Error: {str(e)}")
        finally:
            db_handler.close_connection()

    @task()
    def fetch_missing_data(missing_data):
        if not missing_data:
            logger.info("No missing data to fetch.")
            return None
        
        try:
            data = {}
            indicator_mapping = {}
            for indicator, details in missing_data.items():
                indicator_data, indicator_name = get_world_bank_data(
                    [indicator],
                    details['countries'],
                    details['start_year'],
                    details['end_year'],
                    max_workers=10
                )
                data.update(indicator_data)
                indicator_mapping[indicator] = indicator_name[indicator]
            
            logger.info(f"Successfully fetched missing data for {len(data)} indicators.")
            return {'data': data, 'indicator_mapping': indicator_mapping}
        
        except WorldBankAPIError as e:
            logger.error(f"Error fetching data from World Bank API: {str(e)}")
            raise AirflowException(f"World Bank API Error: {str(e)}")
        except DataProcessingError as e:
            logger.error(f"Error processing World Bank data: {str(e)}")
            raise AirflowException(f"Data Processing Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in fetch_missing_data: {str(e)}")
            raise AirflowException(f"Unexpected error: {str(e)}")

    @task()
    def update_database(pipeline_result):
        if pipeline_result is None:
            logger.info("No new data to update in the database.")
            return False
        
        try:
            data = pipeline_result['data']
            indicator_mapping = pipeline_result['indicator_mapping']
            
            db_handler = MongoDBHandler()
            updates_made = False
            
            for indicator, df in data.items():
                if not df.empty:
                    try:
                        db_handler.insert_or_update_indicator_data(
                            indicator, 
                            indicator_mapping[indicator], 
                            df.reset_index().to_dict('records')
                        )
                        updates_made = True
                        logger.info(f"Successfully updated data for indicator: {indicator}")
                    except Exception as e:
                        logger.error(f"Error updating database for indicator {indicator}: {str(e)}")
                else:
                    logger.info(f"No new data for indicator {indicator}")
            
            return updates_made
        except Exception as e:
            logger.error(f"Unexpected error in update_database: {str(e)}")
            raise AirflowException(f"Database Update Error: {str(e)}")
        finally:
            db_handler.close_connection()

    @task()
    def generate_dashboard(updates_made):
        if not updates_made:
            logger.info("No new data available. Dashboard not updated.")
            return
        
        try:
            db_handler = MongoDBHandler()
            indicator_codes = get_all_indicator_codes()
            countries = ["all"]
            start_year = 1960
            end_year = datetime.now().year - 1
            
            data = {}
            indicator_mapping = {}
            for indicator in indicator_codes:
                indicator_data = db_handler.get_indicator_data(indicator, countries, start_year, end_year)
                if indicator_data:
                    df = pd.DataFrame(indicator_data)
                    df = df.set_index(['country_name', 'country_code', 'year'])
                    data[indicator] = df
                    indicator_mapping[indicator] = db_handler.get_indicator_name(indicator)
                else:
                    logger.warning(f"No data retrieved for indicator {indicator}")
            
            if data:
                dashboard = create_dashboard(data, indicator_mapping)
                run_dashboard(dashboard)
                logger.info("Dashboard updated with new data")
            else:
                logger.warning("No data available to update the dashboard")
        except Exception as e:
            logger.error(f"Error generating dashboard: {str(e)}")
            raise AirflowException(f"Dashboard Generation Error: {str(e)}")
        finally:
            db_handler.close_connection()

    missing_data = check_missing_data()
    pipeline_result = fetch_missing_data(missing_data)
    updates_made = update_database(pipeline_result)
    generate_dashboard(updates_made)

world_bank_data_pipeline_dag = world_bank_data_pipeline()