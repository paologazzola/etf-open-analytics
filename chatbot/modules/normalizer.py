# chatbot/modules/normalizer.py
from __future__ import annotations
from typing import Literal, List, Dict, Any
from .llm import chat_completion

SourceType = Literal["portfolio_evaluator", "rag", "llm"]

# System message to enforce tone, style, and language.
SYSTEM = (
    "You are an assistant for ETF portfolios. Reply in English with a clear, "
    "professional but friendly tone. Keep it concise: 3–6 sentences. "
    "Do not mention JSON or technical field names."
)

def _safe(val: Any) -> str:
    """Safely stringify values for prompt construction."""
    try:
        return str(val)
    except Exception:
        return ""

def _build_prompt_for_model(payload: Dict[str, Any], user_text: str) -> str:
    """
    Expected payload:
      {
        "result": {
          "overall_risk": "low|medium|high",
          "features": {
            "volatility": float,
            "asset_class": str,
            "region": str,
            "replication_method": str
          }
        }
      }
    """
    res = payload.get("result", {}) or {}
    risk = res.get("overall_risk", "?")
    feats = res.get("features", {}) or {}
    vol = feats.get("volatility", None)
    asset = feats.get("asset_class", None)
    region = feats.get("region", None)
    repl = feats.get("replication_method", None)

    # Compact instruction to turn model outputs into a user-facing explanation.
    lines = [
        "Turn the following portfolio risk data into a clear, user-friendly explanation.",
        "Avoid jargon; explain WHY the risk level is assessed that way and, if helpful, add one practical suggestion.",
        f"Overall risk: {risk}",
        f"Annualized volatility: {vol}",
        f"Dominant asset class: {asset}",
        f"Region: {region}",
        f"Replication method: {repl}",
        f"User message (original): {user_text}",
    ]
    return "\n".join(lines)

def _build_prompt_for_rag(payload: Dict[str, Any], user_text: str) -> str:
    """
    Expected payload:
      {
        "answer": "<string>",
        "sources": [ {"path": "..."} | {"meta": {...}} | {"source": "..."} | ... ]
      }
    """
    raw_answer = _safe(payload.get("answer", ""))
    sources = payload.get("sources", []) or []

    # Synthesize up to two soft references to sources in a descriptive way (no links).
    refs: List[str] = []
    for s in sources:
        if isinstance(s, dict):
            path = s.get("path") or s.get("meta", {}).get("path") or s.get("source")
        else:
            path = _safe(s)
        if path:
            refs.append(_safe(path))
        if len(refs) >= 2:
            break

    prompt_parts = [
        "Rewrite the following draft into a clear, self-contained English answer.",
        "If useful, briefly acknowledge up to two sources descriptively (no URLs, no bullet lists).",
        f"Draft answer:\n{raw_answer}",
    ]
    if refs:
        prompt_parts.append(
            f"Considered sources (describe briefly, do not list): {', '.join(refs)}"
        )
    prompt_parts.append(f"User question (original): {user_text}")
    return "\n".join(prompt_parts)

def _build_prompt_for_llm(payload: Dict[str, Any], user_text: str) -> str:
    """
    Expected payload:
      { "text": "<string>" }
    """
    text = _safe(payload.get("text", ""))
    return (
        "Rewrite the following text in clear English, 3–6 sentences, avoiding unnecessary jargon.\n"
        f"Input text:\n{text}\n"
        f"User message (original): {user_text}"
    )

def normalize_response(
    source: SourceType,
    payload: Dict[str, Any],
    user_text: str,
) -> Dict[str, str]:
    """
    Always returns: { 'message': '<human-friendly text>', 'source': '<source>' }
    If the LLM fails, return a deterministic fallback to avoid breaking the UX.
    """
    try:
        if source == "portfolio_evaluator":
            prompt = _build_prompt_for_model(payload, user_text)
        elif source == "rag":
            prompt = _build_prompt_for_rag(payload, user_text)
        else:  # "llm"
            prompt = _build_prompt_for_llm(payload, user_text)

        message = chat_completion(
            prompt=prompt, system=SYSTEM, temperature=0.2, top_p=0.9
        )
        if not message:
            raise RuntimeError("empty LLM message")
        return {"message": message.strip(), "source": source}

    except Exception:
        # Minimal textual fallback so the API contract is never broken.
        if source == "portfolio_evaluator":
            res = payload.get("result", {}) or {}
            risk = res.get("overall_risk", "?")
            feats = res.get("features", {}) or {}
            msg = (
                f"Portfolio risk assessment: {risk}. "
                f"Key factors considered: volatility={feats.get('volatility')}, "
                f"asset_class={feats.get('asset_class')}, region={feats.get('region')}, "
                f"replication={feats.get('replication_method')}."
            )
        elif source == "rag":
            base = _safe(payload.get("answer", "")) or \
                   "I couldn’t generate a complete answer at the moment."
            msg = f"{base}"
        else:
            msg = _safe(payload.get("text", "")) or \
                  "I ran into an issue while formulating the response."

        msg += " (Note: automatic fallback applied.)"
        return {"message": msg, "source": source}
