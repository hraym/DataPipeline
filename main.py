import asyncio
import argparse
from src.pipeline import get_world_bank_data
from src.dashboard import create_dashboard, run_dashboard
from src.indicators_config import indicators, get_all_indicator_codes, get_theme_for_indicator

async def fetch_data(indicator_codes, countries, start_year, end_year):
    return await get_world_bank_data(indicator_codes, countries, start_year, end_year)

def main():
    parser = argparse.ArgumentParser(description="Fetch World Bank data and visualize it.")
    parser.add_argument("--indicators", nargs="+", choices=get_all_indicator_codes(), help="List of indicator codes (optional)")
    parser.add_argument("--countries", nargs="+", required=True, help="List of country codes")
    parser.add_argument("--start_year", type=int, default=2000, help="Start year for data retrieval")
    parser.add_argument("--end_year", type=int, default=2020, help="End year for data retrieval")
    parser.add_argument("--visualize", action="store_true", help="Run the visualization dashboard")
    
    args = parser.parse_args()

    if not args.indicators:
        args.indicators = get_all_indicator_codes()

    # Run the async function to fetch data
    data, indicator_mapping = asyncio.run(fetch_data(args.indicators, args.countries, args.start_year, args.end_year))

    if not args.visualize:
        for indicator, df in data.items():
            print(f"\nData for {indicator} ({indicator_mapping.get(indicator, indicator)}):")
    
    if args.visualize:
        run_dashboard(data, indicators, indicator_mapping)

if __name__ == "__main__":
    main()