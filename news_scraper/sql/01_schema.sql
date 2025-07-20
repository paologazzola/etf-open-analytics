CREATE TABLE market_news_event (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    source TEXT,
    url TEXT UNIQUE,
    published_at TIMESTAMP,
    sentiment_label TEXT,
    sentiment_score FLOAT,
    sentiment_weight FLOAT,
    predicted_impact_date DATE
);
