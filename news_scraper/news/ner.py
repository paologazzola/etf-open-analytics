from typing import Optional
import re
from datetime import datetime, timedelta

def extract_temporal_info(text: str, nlp) -> Optional[str]:
    """
    Extracts a relevant future date from the text using spaCy and filters out past-tense sentences.
    Returns the date in ISO format (YYYY-MM-DD), or None.
    """
    doc = nlp(text)

    for sent in doc.sents:
        has_past_tense = any(token.tag_ in ("VBD", "VBN") for token in sent if token.pos_ == "VERB")
        
        if has_past_tense:
            continue  # Skip sentences written in past tense

        for ent in sent.ents:
            if ent.label_ == "DATE":
                parsed_date = parse_date_from_text(ent.text)
                if parsed_date:
                    return parsed_date.isoformat()

    return None

def parse_date_from_text(date_str: str) -> Optional[datetime]:
    """Very naive date parser; to be improved with better NLP or dateparser."""
    # Examples: "September 1st", "1st Sept", "01/09/2024"
    try:
        from dateutil.parser import parse
        dt = parse(date_str, fuzzy=True, dayfirst=False)
        if dt > datetime.now():
            return dt
    except Exception:
        pass
    return None
