from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

def get_etfs_to_update(field_name: str = "yahoo_symbol"):
    with engine.connect() as conn:
        yesterday = (datetime.utcnow() - timedelta(days=1)).date()
        stmt = text(f"""
            SELECT id, {field_name}, last_price_date
            FROM etf
            WHERE {field_name} IS NOT NULL AND (last_price_date IS NULL OR last_price_date < :yesterday)
        """)
        result = conn.execute(stmt, {"yesterday": yesterday})
        return result.fetchall()

def insert_etf_prices(etf_id: int, prices: list[dict]):
    """Insert daily prices into the etf_price table, including log returns."""
    with engine.begin() as conn:
        for p in prices:
            conn.execute(text("""
                INSERT INTO etf_price (etf_id, date, open, high, low, close, volume, log_return)
                VALUES (:etf_id, :date, :open, :high, :low, :close, :volume, :log_return)
                ON CONFLICT (etf_id, date) DO NOTHING
            """), {
                "etf_id": etf_id,
                "date": p["date"],
                "open": p["open"],
                "high": p["high"],
                "low": p["low"],
                "close": p["close"],
                "volume": p.get("volume", 0),
                "log_return": p.get("log_return")  # can be None if not provided
            })


def update_last_price_date(etf_id: int, last_date):
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE etf SET last_price_date = :last_date WHERE id = :etf_id
        """), {"etf_id": etf_id, "last_date": last_date})