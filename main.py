import asyncio
import argparse
from datetime import datetime
from src.pipeline import get_world_bank_data
from src.dashboard import create_dashboard, run_dashboard
from src.indicators_config import indicators, get_all_indicator_codes, get_theme_for_indicator

def main():
    current_year = datetime.now().year
    
    parser = argparse.ArgumentParser(description="Fetch World Bank data and visualize it.")
    parser.add_argument("--indicators", nargs="+", help="List of indicator codes (optional)")
    parser.add_argument("--countries", nargs="+", help="List of country codes (optional)")
    parser.add_argument("--start_year", type=int, default=2000, help="Start year for data retrieval (default: 2000)")
    parser.add_argument("--end_year", type=int, default=current_year, help="End year for data retrieval (default: current year)")
    parser.add_argument("--visualize", action="store_true", help="Run the visualization dashboard")
    parser.add_argument("--max_workers", type=int, default=10, help="Maximum number of concurrent requests")
    
    args = parser.parse_args()

    # Set default indicators if not provided
    if not args.indicators:
        args.indicators = get_all_indicator_codes()

    # Set default countries to all countries if not provided
    if not args.countries:
        args.countries = ["all"]  # World Bank API uses "all" to fetch data for all countries

    # Fetch data using the batch processing pipeline
    data, indicator_mapping = get_world_bank_data(args.indicators, args.countries, args.start_year, args.end_year, args.max_workers)

    if not args.visualize:
        for indicator, df in data.items():
            print(f"\nData for {indicator} ({indicator_mapping.get(indicator, indicator)}):")
            print(df)
    
    if args.visualize:
        run_dashboard(data, indicators, indicator_mapping)

if __name__ == "__main__":
    main()