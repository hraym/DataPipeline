import asyncio
import argparse
import logging
from datetime import datetime
from src.pipeline import get_world_bank_data
from src.dashboard import create_dashboard, run_dashboard
from src.indicators_config import indicators, get_all_indicator_codes, get_theme_for_indicator
from src.api import WorldBankAPI

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    current_year = datetime.now().year
    
    parser = argparse.ArgumentParser(description="Fetch World Bank data and visualize it.")
    parser.add_argument("--indicators", nargs="+", help="List of indicator codes (optional)")
    parser.add_argument("--countries", nargs="+", help="List of country codes (optional)")
    parser.add_argument("--start_year", type=int, default=2000, help="Start year for data retrieval (default: 2000)")
    parser.add_argument("--end_year", type=int, default=2023, help="End year for data retrieval (default: current year)")
    parser.add_argument("--visualize", action="store_true", help="Run the visualization dashboard")
    parser.add_argument("--max_workers", type=int, default=10, help="Maximum number of concurrent requests")
    
    args = parser.parse_args()

    # Set default indicators if not provided
    if not args.indicators:
        args.indicators = get_all_indicator_codes()

    # Set default countries to all countries if not provided
    if not args.countries:
        args.countries = ["all"]  # World Bank API uses "all" to fetch data for all countries

    # Test API connection
    api = WorldBankAPI('https://api.worldbank.org/v2', max_workers=args.max_workers)
    if not api.test_connection():
        logger.error("Failed to connect to the World Bank API. Please check your internet connection and try again.")
        return

    # Fetch data using the batch processing pipeline
    try:
        logger.info("Starting data retrieval process...")
        data, indicator_mapping = get_world_bank_data(args.indicators, args.countries, args.start_year, args.end_year, args.max_workers)
        
        if not args.visualize:
            for indicator_code, df in data.items():
                logger.info(f"\nData for {indicator_code} ({indicator_mapping.get(indicator_code, indicator_code)}):")
                logger.info(f"\n{df}")
        
        if args.visualize:
            run_dashboard(data, indicators, indicator_mapping)
        
        logger.info("Data retrieval and processing completed successfully.")
    except Exception as e:
        logger.exception(f"An error occurred during data retrieval and processing: {str(e)}")

if __name__ == "__main__":
    main()