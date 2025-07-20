import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import spacy

from news.sentiment import analyze_sentiment
from news.ner import extract_temporal_info
from news.db import insert_news_event
from news.fetch import fetch_economic_news

# Load environment variables
load_dotenv()

# Setup
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# Load NLP models
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
nlp = spacy.load("en_core_web_sm")

def fetch_and_store_news():
    print("Fetching news...")

    news_items = fetch_economic_news(
        query='etf OR "exchange traded fund" OR stock OR stocks OR equities OR bond OR bonds OR "fixed income" OR "stock market" OR "financial markets"',
        page_size=100,
        from_date=datetime.now() - timedelta(days=20),
    )

    with engine.begin() as conn:
        for article in news_items:
            url = article["url"]
            title = article["title"]
            description = article["description"]
            content = article["content"]
            source = article["source_name"]
            published_at = article["published_at"]

            # Check for duplicates
            result = conn.execute(
                text("SELECT 1 FROM market_news_event WHERE url = :url"),
                {"url": url}
            ).fetchone()

            if result:
                print(f"Skipping duplicate: {url}")
                continue

            # Extract temporal info and check if it's present
            # If no date is found, we skip the article
            impact_date = extract_temporal_info(content, nlp)
            if impact_date is None:
                print(f"No date found for article: {title[:100]}...")
                continue

            # Analyze sentiment
            label, score, weight = analyze_sentiment(article.get("description", ""), article.get("content", ""))

            # Extract temporal info
            impact_date = extract_temporal_info(content, nlp)

            # Insert news
            insert_news_event(
                title=title,
                description=description,
                source=source,
                url=url,
                published_at=published_at,
                sentiment_label=label,
                sentiment_score=score,
                sentiment_weight=weight,
                predicted_impact_date=impact_date
            )
            print(f"Inserted news: {title} (sentiment: {label}, score: {score:.2f}, date: {impact_date})")

if __name__ == "__main__":
    fetch_and_store_news()
