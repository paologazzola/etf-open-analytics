"""
Portfolio evaluation module for ETF Open Analytics Chatbot.

This module replicates the same feature engineering logic
used in the original portfolio_evaluator training pipeline.

The model expects the following features:
- volatility (float)
- asset_class (categorical)
- region (categorical)
- replication_method (categorical)

Author: Chatbot AI Assistant
"""

from __future__ import annotations
import os
import numpy as np
import pandas as pd
import joblib
from typing import List, Dict
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------
# Model and Database Initialization
# --------------------------------------------------------
MODEL_PATH = os.getenv(
    "RISK_MODEL_PATH",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "portfolio_evaluator", "models", "risk_model.pkl")),
)
model = joblib.load(MODEL_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables.")
ENGINE = create_engine(DATABASE_URL)


# --------------------------------------------------------
# Database queries aligned with your schema
# --------------------------------------------------------
def load_etf_data(isins: List[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load ETF metadata and daily price data for the given ISINs."""
    q_meta = text("""
        SELECT
            e.id,
            e.isin,
            e.name,
            e.region,
            e.replication_method,
            e.asset_class
        FROM etf e
        WHERE e.isin = ANY(:isins)
    """)
    meta = pd.read_sql(q_meta, ENGINE, params={"isins": isins})

    q_px = text("""
        SELECT
            e.isin,
            p.date,
            p.close,
            p.log_return
        FROM etf_price p
        JOIN etf e ON e.id = p.etf_id
        WHERE e.isin = ANY(:isins)
        ORDER BY e.isin, p.date
    """)
    px = pd.read_sql(q_px, ENGINE, params={"isins": isins})
    return meta, px


# --------------------------------------------------------
# Feature computation
# --------------------------------------------------------
def compute_volatility(px: pd.DataFrame, isin: str) -> float:
    """Compute annualized volatility from log returns (or close prices if missing)."""
    grp = px.loc[px["isin"] == isin].sort_values("date").copy()
    if grp.empty:
        return 0.0

    if "log_return" not in grp.columns or grp["log_return"].isna().all():
        grp["log_return"] = np.log(grp["close"] / grp["close"].shift(1))

    valid = grp["log_return"].dropna()
    if len(valid) < 2:
        return 0.0

    vol = valid.std() * np.sqrt(252)
    return float(vol if np.isfinite(vol) else 0.0)


def weighted_mode(values: pd.Series, weights: Dict[str, float]) -> str:
    """Compute weighted mode for categorical variables."""
    weighted_counts = {}
    for isin, val in values.items():
        w = weights.get(isin, 0)
        if not isinstance(val, str):
            continue
        weighted_counts[val] = weighted_counts.get(val, 0) + w
    if not weighted_counts:
        return "unknown"
    return max(weighted_counts, key=weighted_counts.get)


def make_features(meta: pd.DataFrame, px: pd.DataFrame, portfolio: List[Dict]) -> pd.DataFrame:
    """
    Build features consistent with model training:
    volatility, asset_class, region, replication_method
    """
    if meta.empty:
        raise ValueError("No ETF metadata found.")
    if px.empty:
        raise ValueError("No ETF price data found.")

    total = sum(p["amount"] for p in portfolio) or 1.0
    weights = {p["isin"]: p["amount"] / total for p in portfolio}

    # compute volatility for each isin
    vol_map = {isin: compute_volatility(px, isin) for isin in meta["isin"].unique()}

    # weighted average volatility
    portfolio_vol = sum(weights.get(isin, 0) * vol_map.get(isin, 0) for isin in vol_map)

    # weighted modes for categoricals
    meta_indexed = meta.set_index("isin")
    asset_class = weighted_mode(meta_indexed["asset_class"], weights)
    region = weighted_mode(meta_indexed["region"], weights)
    replication_method = weighted_mode(meta_indexed["replication_method"], weights)

    # final single-row DataFrame
    return pd.DataFrame([{
        "volatility": float(portfolio_vol),
        "asset_class": asset_class,
        "region": region,
        "replication_method": replication_method
    }])


# --------------------------------------------------------
# Portfolio evaluation
# --------------------------------------------------------
def evaluate_portfolio(portfolio: List[Dict]) -> Dict:
    """
    Evaluate portfolio risk using the pre-trained Pipeline model.

    The model already includes its own preprocessing (OneHotEncoder).
    """
    isins = [p["isin"] for p in portfolio]
    meta, px = load_etf_data(isins)
    X = make_features(meta, px, portfolio)

    # --- Debug (uncomment to inspect)
    # print("Features passed to model:\n", X.to_dict(orient='records'))

    predicted_risk = model.predict(X)[0]  # "low" | "medium" | "high"

    return {
        "overall_risk": predicted_risk,
        "features": X.to_dict(orient="records")[0],
    }


# --------------------------------------------------------
# Manual test
# --------------------------------------------------------
if __name__ == "__main__":
    test_portfolio = [
        {"isin": "CH1129538448", "amount": 20},
        {"isin": "IE00B3XXRP09", "amount": 80},
    ]
    result = evaluate_portfolio(test_portfolio)
    print(result)


# ----------------------------
# Quick test
# ----------------------------
if __name__ == "__main__":
    test_portfolio = [
        {"isin": "CH1129538448", "amount": 20},
        {"isin": "IE00B3XXRP09", "amount": 80},
    ]
    print(evaluate_portfolio(test_portfolio))
