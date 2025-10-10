import yfinance as yf
import pandas as pd
from datetime import datetime
import numpy as np

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

        # Fix multi-index if needed
        if isinstance(df.columns, pd.MultiIndex):
            df = df.swaplevel(axis=1)[yahoo_symbol]

        # Calculate log returns
        df['log_return'] = np.log(df['Close'] / df['Close'].shift(1))

        prices = []
        for date, row in df.iterrows():
            # Skip first row (NaN log return)
            if pd.isna(row["log_return"]):
                continue
            prices.append({
                "date": date.date(),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
                "log_return": float(row["log_return"])
            })
        return prices

    except Exception as e:
        print(f"Error fetching data for {yahoo_symbol}: {e}")
        return []
