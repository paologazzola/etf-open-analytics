# chatbot/main.py
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modules.router import parse_portfolio
from modules.portfolio_tool import evaluate_portfolio
from modules.rag import answer_with_rag
from modules.normalizer import normalize_response
from models.standard_response import StandardResponse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application
app = FastAPI(title="ETF Open Analytics Chatbot")

class ChatRequest(BaseModel):
    """Schema for incoming chat requests."""
    message: str

@app.get("/health")
def health():
    """Simple health-check endpoint."""
    return {"status": "ok"}

@app.post("/chat", response_model=StandardResponse)
def chat(req: ChatRequest):
    """
    Main chat endpoint.
    Depending on the content of the user message:
      - If an ETF portfolio is detected, the request is routed to the model evaluator.
      - Otherwise, it falls back to the RAG (retrieval-augmented generation) flow.
    In all cases, the output is normalized into a consistent response format.
    """
    text = req.message.strip()

    # --- 1) Try to extract a portfolio → MODEL path
    portfolio = parse_portfolio(text)
    if portfolio:
        try:
            result = evaluate_portfolio(portfolio)
        except Exception as e:
            # Preserve the error semantics but return a proper HTTP error
            raise HTTPException(status_code=400, detail=str(e))

        # Normalize to a human-readable message
        return normalize_response(
            source="portfolio_evaluator",
            payload={"result": result},
            user_text=text,
        )

    # --- 2) Otherwise → RAG path
    answer, sources = answer_with_rag(text)

    return normalize_response(
        source="rag",
        payload={"answer": answer, "sources": sources},
        user_text=text,
    )
