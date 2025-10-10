import os
import psycopg2
import logging
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import date, timedelta
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        logger.error("DATABASE_URL not defined in environment")
        raise RuntimeError("DATABASE_URL not defined")
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.exception("Failed to connect to database")
        raise

def get_etf_details_with_log_returns(investments: List[Dict]) -> List[Dict]:
    """
    For each ISIN + amount, fetch ETF id and info from DB, including last 3 years of log_return.
    Returns a list of dicts with: isin, amount, asset_class, region, replication_method, log_returns[]
    """
    start_date = (date.today() - timedelta(days=3 * 365)).isoformat()
    enriched = []

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for entry in investments:
                    isin = entry["isin"]
                    amount = entry["amount"]

                    cur.execute("""
                        SELECT id, asset_class, region, replication_method
                        FROM etf
                        WHERE isin = %s
                    """, (isin,))
                    etf_row = cur.fetchone()

                    if not etf_row:
                        logger.warning(f"ISIN not found in DB: {isin}")
                        continue

                    etf_id = etf_row["id"]

                    cur.execute("""
                        SELECT log_return
                        FROM etf_price
                        WHERE etf_id = %s AND date >= %s AND log_return IS NOT NULL
                        ORDER BY date ASC
                    """, (etf_id, start_date))
                    log_returns = [float(r["log_return"]) for r in cur.fetchall()]

                    enriched.append({
                        "isin": isin,
                        "amount": amount,
                        "asset_class": etf_row["asset_class"],
                        "region": etf_row["region"],
                        "replication_method": etf_row["replication_method"],
                        "log_returns": log_returns
                    })
    except Exception as e:
        logger.exception("Error while retrieving ETF details")
        raise

    return enriched

def load_training_data(since_date: str) -> List[Dict]:
    """
    Retrieve ETF data with log_returns since the specified date.
    Returns a list of dicts with:
        volatility: float,
        asset_class: str,
        region: str,
        replication_method: str,
        risk: str
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        ep.log_return,
                        e.asset_class,
                        e.region,
                        e.replication_method
                    FROM etf_price ep
                    JOIN etf e ON e.id = ep.etf_id
                    WHERE ep.date > %s AND ep.log_return IS NOT NULL
                """, (since_date,))
                rows = cur.fetchall()
                data = []
                for row in rows:
                    volatility = abs(float(row["log_return"]))  # simple proxy for volatility
                    if volatility >= 0.03:
                        risk = "high"
                    elif volatility >= 0.015:
                        risk = "medium"
                    else:
                        risk = "low"
                    data.append({
                        "volatility": volatility,
                        "asset_class": row["asset_class"],
                        "region": row["region"],
                        "replication_method": row["replication_method"],
                        "risk": risk
                    })
                return data
    except Exception as e:
        logger.exception("Error while loading training data from DB")
        raise
