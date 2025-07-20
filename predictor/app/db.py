import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, timedelta

# Load the database connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Custom exception for missing ETF
class EtfNotFoundError(Exception):
    pass

# Establish a connection to the PostgreSQL database
def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not defined in the environment")
    return psycopg2.connect(DATABASE_URL)

# Retrieve the internal ETF ID using the provided ISIN
def get_etf_id_by_isin(isin: str) -> int:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM etf WHERE isin = %s", (isin,))
            result = cur.fetchone()
            if result is None:
                raise EtfNotFoundError(f"ETF with ISIN '{isin}' not found")
            return result[0]

# Retrieve log returns starting from (today - days), ordered by date
def get_etf_prices_with_log_return(etf_id: int, days: int):
    start_date = (date.today() - timedelta(days=days)).isoformat()
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT date, log_return, close
                FROM etf_price
                WHERE etf_id = %s AND date >= %s AND log_return IS NOT NULL
                ORDER BY date ASC
            """, (etf_id, start_date))
            return cur.fetchall()
        
