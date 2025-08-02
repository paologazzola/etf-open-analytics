from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.portfolio_risk_evaluator import evaluate_portfolio

app = FastAPI()

class EtfInvestment(BaseModel):
    isin: str = Field(..., description="ETF ISIN code")
    amount: float = Field(..., gt=0, description="Amount invested in this ETF")

class PortfolioRequest(BaseModel):
    portfolio: List[EtfInvestment]

@app.post("/portfolio/risk")
def assess_risk(request: PortfolioRequest):
    try:
        data = [{"isin": e.isin, "amount": e.amount} for e in request.portfolio]
        result = evaluate_portfolio(data)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
