import asyncio
import argparse
from src.pipeline import get_world_bank_data

async def main(indicator_codes: list, countries: list, start_year: int, end_year: int):
    data = await get_world_bank_data(indicator_codes, countries, start_year, end_year)
    
    for indicator, df in data.items():
        print(f"\nData for {indicator}:")
        print(df.head())
    
    # Add any additional processing or saving logic here

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch World Bank data for specified indicators and countries.")
    parser.add_argument("--indicators", nargs="+", required=True, help="List of indicator codes")
    parser.add_argument("--countries", nargs="+", required=True, help="List of country codes")
    parser.add_argument("--start_year", type=int, default=1960, help="Start year for data retrieval")
    parser.add_argument("--end_year", type=int, help="End year for data retrieval")

    args = parser.parse_args()

    asyncio.run(main(args.indicators, args.countries, args.start_year, args.end_year))