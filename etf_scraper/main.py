from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from etf.db import get_etfs_to_update, insert_etf_prices, update_last_price_date
from etf.fetch import fetch_etf_prices

# Load environment variables from .env file
load_dotenv()

def update_all_prices():
    # Use environment variable to determine which ticker field to use (e.g., yahoo_symbol)
    ticker_field = os.getenv("TICKER_FIELD", "yahoo_symbol")

    # Retrieve ETFs that need price updates based on the specified ticker field
    etfs = get_etfs_to_update(field_name=ticker_field)
    if not etfs:
        print("All ETFs are up to date.")
        return

    for etf in etfs:
        etf_id, symbol_value, last_date = etf

        # Determine the start date for fetching prices
        if last_date is None:
            # If no previous data, start from year 2000
            from_date = datetime(2000, 1, 1)
        else:
            # Otherwise, start from the day after the last saved date
            from_date = datetime.combine(last_date + timedelta(days=1), datetime.min.time())

        # fetch data until today
        to_date = datetime.now()

        print(f"Fetching {symbol_value} from {from_date.date()} to {to_date.date()}...")

        prices = fetch_etf_prices(symbol_value, from_date, to_date)
        if prices:
            insert_etf_prices(etf_id, prices)
            latest = max([p["date"] for p in prices])
            update_last_price_date(etf_id, latest)
            print(f"Updated {len(prices)} records for {symbol_value}")
        else:
            print(f"No data found for {symbol_value}")

if __name__ == "__main__":
    update_all_prices()
