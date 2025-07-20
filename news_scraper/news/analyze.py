from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from transformers import AutoModelForTokenClassification
from transformers import AutoTokenizer as TokenClassifierTokenizer
from datetime import datetime
import spacy

# Load FinBERT for sentiment
sent_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
sent_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
sent_pipeline = pipeline("sentiment-analysis", model=sent_model, tokenizer=sent_tokenizer)

# NER model for DATE extraction
ner_model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
ner_tokenizer = TokenClassifierTokenizer.from_pretrained("dslim/bert-base-NER")
ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer, aggregation_strategy="simple")

# spaCy fallback
import en_core_web_sm
spacy_nlp = en_core_web_sm.load()

def extract_future_date(text):
    # Use NER to extract dates
    entities = ner_pipeline(text[:512])
    dates = [e["word"] for e in entities if e["entity_group"] == "DATE"]
    # Try parsing the first future date via spaCy fallback
    doc = spacy_nlp(text)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            dates.append(ent.text)
    # Return first valid future date normalized to ISO, else None
    for raw in dates:
        try:
            dt = datetime.fromisoformat(raw)
            if dt.date() >= datetime.today().date():
                return dt.date()
        except ValueError:
            pass
    return None

def analyze_articles(articles):
    results = []
    for art in articles:
        text = art.get("title", "") + ". " + art.get("content", "")
        sentiment = sent_pipeline(text[:512])[0]
        future_date = extract_future_date(text)
        results.append({
            "title": art["title"],
            "url": art["url"],
            "published_at": art["published_at"],
            "sentiment": sentiment["label"].lower(),
            "sentiment_score": float(sentiment["score"]),
            "extracted_date": str(future_date) if future_date else None,
        })
    return results
