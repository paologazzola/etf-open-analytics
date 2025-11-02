"""
Router utilities for intent detection and portfolio extraction.

This module focuses on robustly extracting a minimal portfolio from free text.
If at least one valid ISIN and a (nearby) amount are found, we return a list of
{"isin": str, "amount": float} entries. Otherwise, we return None and the app
will fall back to RAG.

Design goals:
- Keep dependencies minimal (regex and stdlib only).
- Be locale-agnostic for numbers: handle "," and "." as separators.
- Greedy "closest-number" assignment without reusing the same number twice.

Examples accepted:
- "Invest 1000 EUR on CH1129538448 and 200 on IE00BK5BQV03"
- "CH1129538448 750, IE00BK5BQV03 1.250,00"
- "60% CH1129538448, 40% IE00BK5BQV03" (percentages become amounts)
- "100k on CH..., 2.5k on IE..." (k/m suffixes supported)
"""
from __future__ import annotations
import re
from typing import List, Dict, Optional, Tuple

# Conservative ISIN regex: 2 letters + 9 alnum + 1 digit (checksum not verified here)
ISIN_RE = re.compile(r"\b([A-Z]{2}[A-Z0-9]{9}\d)\b")

# Number tokens, capture the numeric core and optional suffix.
# Supports thousand & decimal separators (both . and ,), and k/m suffix.
NUM_TOKEN_RE = re.compile(
    r"(?P<prefix>[$€£]?)\s*"  # optional currency symbol
    r"(?P<num>(?:\d{1,3}([.,]\d{3})+|\d+)(?:[.,]\d{1,4})?)"  # grouped number
    r"\s*(?P<suffix>k|m|K|M|\%)?"  # optional suffix (k, m, or %)
)

# Currency words kept for context only (not currently used, reserved for future rules)
CURRENCY_WORDS = {"eur", "euro", "euros", "usd", "dollars", "chf", "gbp"}


def _parse_numeric_token(token: str, suffix: Optional[str]) -> Optional[float]:
    """Parse a numeric token into a float, handling locale-like separators and k/m/% suffixes.

    Rules:
    - If both "," and "." appear, treat the rightmost symbol as decimal separator, remove the other.
    - If only one appears and there are <= 2 digits after it -> decimal, else thousands.
    - Suffix 'k' or 'K' multiplies by 1e3, 'm' or 'M' by 1e6.
    - Suffix '%' divides by 100 (so 60% -> 0.6).
    """
    s = token.replace(" ", "")
    has_dot = "." in s
    has_comma = "," in s

    if has_dot and has_comma:
        # Use the rightmost as decimal separator
        last_dot = s.rfind(".")
        last_comma = s.rfind(",")
        if last_dot > last_comma:
            # dot is decimal; remove commas
            s = s.replace(",", "")
        else:
            # comma is decimal; remove dots and replace comma with dot
            s = s.replace(".", "")
            s = s.replace(",", ".")
    elif has_comma and not has_dot:
        # Decide if comma is decimal: if <= 2 digits after, assume decimal
        parts = s.split(",")
        if len(parts[-1]) <= 2:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    else:
        # Only dots or none: remove thousand dots by default; keep decimal dot
        if has_dot:
            parts = s.split(".")
            if len(parts) > 2:
                # many dots -> remove all but last
                s = "".join(parts[:-1]) + "." + parts[-1]

    try:
        val = float(s)
    except ValueError:
        return None

    if suffix:
        if suffix.lower() == "k":
            val *= 1_000.0
        elif suffix.lower() == "m":
            val *= 1_000_000.0
        elif suffix == "%":
            val /= 100.0
    return val


def _extract_number_spans(text: str) -> List[Tuple[float, int, int]]:
    """Return a list of (value, start, end) for numeric tokens in the text.
    Values are floats with k/m/% applied.
    """
    out: List[Tuple[float, int, int]] = []
    for m in NUM_TOKEN_RE.finditer(text):
        raw = m.group("num")
        suffix = m.group("suffix")
        val = _parse_numeric_token(raw, suffix)
        if val is None:
            continue
        out.append((val, m.start(), m.end()))
    return out


def _extract_isin_spans(text: str) -> List[Tuple[str, int, int]]:
    """Return a list of (isin, start, end) spans (uppercase text for safety)."""
    return [(m.group(1), m.start(1), m.end(1)) for m in ISIN_RE.finditer(text.upper())]


def _assign_amounts_to_isins(text: str, isins: List[Tuple[str, int, int]]) -> Optional[List[Dict[str, float]]]:
    """Greedy nearest-neighbor assignment: for each ISIN, pick the closest unused number.

    If numbers are percentages and *all* numbers look like percentages, we keep them as 0.x values;
    the caller may normalize them downstream.
    """
    nums = _extract_number_spans(text)
    if not nums:
        return None

    used = [False] * len(nums)
    results: List[Dict[str, float]] = []

    for isin, s, e in isins:
        # Find closest unused number by absolute distance in character positions
        best_idx = None
        best_dist = 10**9
        center = (s + e) // 2
        for idx, (val, ns, ne) in enumerate(nums):
            if used[idx]:
                continue
            dist = abs(((ns + ne) // 2) - center)
            if dist < best_dist:
                best_dist = dist
                best_idx = idx
        if best_idx is None:
            continue
        used[best_idx] = True
        results.append({"isin": isin, "amount": float(nums[best_idx][0])})

    return results or None


def _percent_only(entries: List[Dict[str, float]]) -> bool:
    """Heuristic: treat as percent-only if all values are in [0, 1.2] and at least
    one is <= 1.0 (typical when user writes 60% 40% and parser gives 0.6 0.4).
    """
    if not entries:
        return False
    return all(0.0 <= e["amount"] <= 1.2 for e in entries) and any(e["amount"] <= 1.0 for e in entries)


def parse_portfolio(text: str) -> Optional[List[Dict[str, float]]]:
    """Extract portfolio entries from free text.

    Returns a list like [{"isin": "CH1129538448", "amount": 10000.0}, ...] or None.
    If the detected values look like percentages, converts them to normalized weights
    summing to 1.0 so that downstream code can treat them as weights.
    """
    if not text or not text.strip():
        return None

    upper = text.upper()
    isins = _extract_isin_spans(upper)
    if not isins:
        return None

    entries = _assign_amounts_to_isins(text, isins)
    if not entries:
        return None

    # If user provided percentages (e.g., 60% 40%), amounts will be 0.6 and 0.4.
    if _percent_only(entries):
        total = sum(e["amount"] for e in entries) or 1.0
        entries = [{"isin": e["isin"], "amount": e["amount"] / total} for e in entries]

    return entries


# Optional: lightweight intent classifier
PORTFOLIO_KEYWORDS = {"portfolio", "weights", "invest", "allocation", "amount", "valuta", "valutare"}


def classify_intent(text: str) -> str:
    """Very small rule-based classifier used by the API layer (optional).
    Returns "portfolio_eval" if we detect a parsable portfolio or keywords, else "general".
    """
    if parse_portfolio(text):
        return "portfolio_eval"
    t = text.lower()
    if any(k in t for k in PORTFOLIO_KEYWORDS):
        return "portfolio_eval"
    return "general"
