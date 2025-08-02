import os
import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from app.db import get_etf_details_with_log_returns

load_dotenv()
MODEL_PATH = os.getenv("MODEL_PATH", "models/risk_model.pkl")

RISK_TO_SCORE = {"low": 1, "medium": 2, "high": 3}
SCORE_TO_RISK = {1: "low", 2: "medium", 3: "high"}

def evaluate_portfolio(portfolio):
    """
    Receives a list of {isin, amount} dicts, evaluates each ETF using the model,
    and aggregates risk based on investment weights.
    """
    model = joblib.load(MODEL_PATH)
    enriched_etfs = get_etf_details_with_log_returns(portfolio)

    if not enriched_etfs:
        raise ValueError("No valid ETFs found in portfolio.")

    total_amount = sum(etf["amount"] for etf in enriched_etfs)
    if total_amount == 0:
        raise ValueError("Total invested amount must be greater than zero.")

    risk_results = []
    weighted_score = 0

    for etf in enriched_etfs:
        volatility = float(np.std(etf["log_returns"])) if etf["log_returns"] else 0.0

        features = pd.DataFrame([{
            "volatility": volatility,
            "asset_class": etf["asset_class"],
            "region": etf["region"],
            "replication_method": etf["replication_method"]
        }])

        predicted_risk = model.predict(features)[0]

        weight = etf["amount"] / total_amount
        weighted_score += RISK_TO_SCORE[predicted_risk] * weight

        risk_results.append({
            "isin": etf["isin"],
            "amount": etf["amount"],
            "weight": weight,
            "volatility": round(volatility, 4),
            "predicted_risk": predicted_risk
        })

    avg_score = round(weighted_score)
    overall_risk = SCORE_TO_RISK[avg_score]

    return {
        "overall_risk": overall_risk,
        "etf_details": risk_results
    }
