from fastapi import HTTPException
import numpy as np
import traceback

from app.db import (
    get_etf_id_by_isin,
    get_etf_prices_with_log_return,
    EtfNotFoundError
)
from app.model import predict_next_log_return

def get_prediction_data(isin: str, days: int) -> dict:
    """
    Returns prediction data for a given ETF:
    - current price and its date
    - predicted log return
    - predicted price
    - expected percentage change
    """
    try:
        etf_id = get_etf_id_by_isin(isin)
        prices = get_etf_prices_with_log_return(etf_id, days)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal error while retrieving data")

    if len(prices) < 2:
        raise HTTPException(status_code=400, detail="At least 2 log returns are required for prediction")

    log_returns = [row["log_return"] for row in prices]
    latest_record = prices[-1]  # Most recent due to ORDER BY ASC
    latest_price = float(latest_record["close"])
    latest_date = latest_record["date"]

    predicted_log_return = predict_next_log_return(log_returns)
    predicted_price = latest_price * np.exp(predicted_log_return)
    percentage_change = (predicted_price - latest_price) / latest_price * 100

    return {
        "isin": isin,
        "days_used": len(log_returns),
        "current_price": latest_price,
        "price_date": latest_date,
        "predicted_log_return": predicted_log_return,
        "predicted_price": predicted_price,
        "percentage_change": percentage_change
    }

