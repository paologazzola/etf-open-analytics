import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), future=True)

def insert_news_event(
    title,
    description,
    source,
    url,
    published_at,
    sentiment_label,
    sentiment_score,
    sentiment_weight,
    predicted_impact_date
):
    with engine.begin() as conn:
        existing = conn.execute(
            text("SELECT 1 FROM market_news_event WHERE url = :url"),
            {"url": url}
        )
        if existing.first():
            print(f"Skipping duplicate: {url}")
            return

        conn.execute(text("""
            INSERT INTO market_news_event (
                title,
                description,
                source,
                url,
                published_at,
                sentiment_label,
                sentiment_score,
                sentiment_weight,
                predicted_impact_date
            )
            VALUES (
                :title,
                :description,
                :source,
                :url,
                :published_at,
                :sentiment_label,
                :sentiment_score,
                :sentiment_weight,
                :predicted_impact_date
            )
        """), {
            "title": title,
            "description": description,
            "source": source,
            "url": url,
            "published_at": published_at,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "sentiment_weight": sentiment_weight,
            "predicted_impact_date": predicted_impact_date
        })

        print(f"Inserted: {title}")
