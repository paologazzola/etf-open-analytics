import os
import requests
from dotenv import load_dotenv

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_ENDPOINT = os.getenv("NEWSAPI_ENDPOINT", "https://newsapi.org/v2/everything")

def fetch_economic_news(query="markets OR stocks OR bonds OR ETF", from_date=None, to_date=None, language="en", page_size=20):
    params = {
        "sources": "bloomberg,cnbc,reuters,fortune,forbes,business-insider,financial-times",
        "q": query,
        "language": language,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": NEWSAPI_KEY
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    response = requests.get(NEWSAPI_ENDPOINT, params=params)
    response.raise_for_status()
    items = response.json().get("articles", [])
    news_data = [{
        "title": a["title"],
        "description": a.get("description", ""),
        "content": a.get("content") or a.get("description") or "",
        "source_name": a["source"]["name"],
        "url": a["url"],
        "published_at": a["publishedAt"]
    } for a in items]
    return news_data
