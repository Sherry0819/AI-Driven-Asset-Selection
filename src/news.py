from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Optional
import os
import requests
import pandas as pd


@dataclass
class NewsItem:
    date: pd.Timestamp
    title: str


def load_news_xlsx(path: str) -> pd.DataFrame:
    """Load headlines from an Excel file with columns: Title, Date."""
    df = pd.read_excel(path)
    df = df.rename(columns={c: c.strip() for c in df.columns})
    if "Title" not in df.columns or "Date" not in df.columns:
        raise ValueError("Expected columns: 'Title' and 'Date'")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
    df = df.dropna(subset=["Date", "Title"]).copy()
    df["Title"] = df["Title"].astype(str)
    return df.sort_values("Date")


def build_news_window(df_news: pd.DataFrame, asof: pd.Timestamp, lookback_days: int = 7) -> str:
    """Return a bullet-list string of headlines within [asof-lookback, asof]."""
    asof = pd.to_datetime(asof, utc=True)
    start = asof - pd.Timedelta(days=lookback_days)
    sub = df_news[(df_news["Date"] > start) & (df_news["Date"] <= asof)]
    # keep latest first
    sub = sub.sort_values("Date", ascending=False)
    return "\n".join(f"- {t}" for t in sub["Title"].tolist())


def fetch_newsapi(query: str, date_from: str, date_to: str, api_key: Optional[str] = None, page_size: int = 100) -> pd.DataFrame:
    """Fetch headlines from NewsAPI 'everything' endpoint for a date range."""
    api_key = api_key or os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise RuntimeError("Missing NEWSAPI_KEY. Set it in env or pass api_key=...")

    url = "https://newsapi.org/v2/everything"
    all_rows = []
    page = 1
    while True:
        params = {
            "q": query,
            "from": date_from,
            "to": date_to,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "page": page,
            "apiKey": api_key,
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        js = r.json()
        articles = js.get("articles", [])
        for a in articles:
            all_rows.append({"Date": a.get("publishedAt"), "Title": a.get("title")})
        total = js.get("totalResults", 0)
        if page * page_size >= total or not articles:
            break
        page += 1

    df = pd.DataFrame(all_rows)
    if df.empty:
        return df
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
    df = df.dropna(subset=["Date", "Title"]).copy()
    df["Title"] = df["Title"].astype(str)
    return df.sort_values("Date")
