"""FastAPI app entrypoint.

POST /chat {"message": "..."}
- If ISINs + amounts are detected, returns a portfolio risk evaluation.
- Else, answers via RAG with retrieved sources.

All helper modules live under `chatbot/modules/`.
"""
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modules.router import parse_portfolio
from modules.portfolio_tool import evaluate_portfolio
from modules.rag import answer_with_rag
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ETF Chatbot (Local, CPU-only)")


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    """Single endpoint for both general chat (RAG) and portfolio risk evaluation."""
    text = req.message.strip()

    # Specialized path: try to extract a portfolio from free text
    portfolio = parse_portfolio(text)
    if portfolio:
        try:
            result = evaluate_portfolio(portfolio)
        except Exception as e:
            # Surface deterministic errors (e.g., missing DB rows, feature mismatch)
            raise HTTPException(status_code=400, detail=str(e))
        return {"type": "portfolio_risk", "result": result}

    # Fallback to RAG over the local knowledge base
    answer, sources = answer_with_rag(text)
    return {"type": "rag", "answer": answer, "sources": sources}