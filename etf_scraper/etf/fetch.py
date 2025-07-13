import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_etf_prices(yahoo_symbol: str, from_date: datetime, to_date: datetime) -> list[dict]:
    try:
        df = yf.download(
            tickers=yahoo_symbol,
            start=from_date.strftime("%Y-%m-%d"),
            end=to_date.strftime("%Y-%m-%d"),
            progress=False
        )

        if df.empty:
            print(f"No data found for {yahoo_symbol}")
            return []

        # If the DataFrame uses a MultiIndex (e.g., columns like ("Close", "VOO")), flatten it
        if isinstance(df.columns, pd.MultiIndex):
            df = df.swaplevel(axis=1)[yahoo_symbol]

        prices = []
        for date, row in df.iterrows():
            prices.append({
                "date": date.date(),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"])
            })
        return prices

    except Exception as e:
        print(f"Error while fetching data for {yahoo_symbol}: {e}")
        return []
