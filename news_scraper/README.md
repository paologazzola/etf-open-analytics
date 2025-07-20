# ETF Open Analytics News Scraper

This project collects, analyzes, and stores financial news related to ETFs, stocks, bonds, and financial markets. It uses NLP and sentiment analysis to extract relevant information and predict the impact date of news events.

## Features

- Fetches news articles from major financial sources using NewsAPI.
- Extracts future impact dates from news content using spaCy and NER models.
- Performs sentiment analysis with FinBERT.
- Stores results in a PostgreSQL database.

## Setup

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Configure environment variables:**
   - Edit `.env` with your `DATABASE_URL` and `NEWSAPI_KEY`.

3. **Database:**
   - Create the schema using [sql/01_schema.sql](sql/01_schema.sql).

## Usage

Run the main script to fetch, analyze, and store news:

```sh
python main.py
```

## File Structure

- `main.py`: Entry point for fetching and storing news.
- `news/`: Contains modules for fetching, analyzing, and storing news.
  - [`news/fetch.py`](news/fetch.py): Fetches news articles.
  - [`news/ner.py`](news/ner.py): Extracts temporal information.
  - [`news/sentiment.py`](news/sentiment.py): Sentiment analysis.
  - [`news/db.py`](news/db.py): Database operations.
  - [`news/analyze.py`](news/analyze.py): Alternative analysis pipeline.
- `sql/01_schema.sql`: Database schema.

## Notes

- Requires Python 3.8+.
- Make sure to install the spaCy model as described above.
- The FinBERT and NER models are downloaded automatically on first run.
