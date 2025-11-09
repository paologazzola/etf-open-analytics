from pydantic import BaseModel
from typing import Literal

class StandardResponse(BaseModel):
    message: str
    source: Literal["portfolio_evaluator", "rag", "llm"]
