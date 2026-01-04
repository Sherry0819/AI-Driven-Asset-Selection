from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from src.news import fetch_newsapi, build_news_window
from src.llm import OllamaClient
from src.portfolio import portfolio_from_llm_output

# NOTE:
# For a full backtest, you need a price source. A simple option is yfinance.
# We keep it optional to avoid forcing internet dependencies.
# You can implement your own price loader (Bloomberg/Refinitiv/WRDS) here.


def main():
    p = argparse.ArgumentParser(description="Full pipeline: fetch news (NewsAPI) + LLM selection + backtest (plug in your price source).")
    p.add_argument("--query", type=str, default="S&P 500 OR earnings OR guidance OR merger OR acquisition")
    p.add_argument("--from_date", type=str, required=True, help="YYYY-MM-DD")
    p.add_argument("--to_date", type=str, required=True, help="YYYY-MM-DD")
    p.add_argument("--rebalance", type=str, default="W-FRI", help="Pandas offset alias, e.g. D, W-FRI, M")
    p.add_argument("--lookback_days", type=int, default=7)
    p.add_argument("--positions", type=int, default=20)
    args = p.parse_args()

    df_news = fetch_newsapi(args.query, args.from_date, args.to_date)
    if df_news.empty:
        raise SystemExit("No news returned. Check query / dates / key.")

    rebalance_dates = pd.date_range(args.from_date, args.to_date, freq=args.rebalance, tz="UTC")
    client = OllamaClient(model="gemma2")

    outdir = Path("reports/full")
    outdir.mkdir(parents=True, exist_ok=True)

    portfolios = []
    for d in rebalance_dates:
        headlines = build_news_window(df_news, asof=d, lookback_days=args.lookback_days)
        if not headlines.strip():
            continue
        raw = client.select_portfolio(headlines_bullets=headlines, universe_hint="S&P 500", n=args.positions)
        w = portfolio_from_llm_output(raw)
        w["rebalance_date"] = d
        portfolios.append(w)

    if not portfolios:
        raise SystemExit("No portfolios formed (not enough headlines within windows).")

    df_w = pd.concat(portfolios, ignore_index=True)
    df_w.to_csv(outdir / "portfolios.csv", index=False)

    print("Saved portfolios. Next: plug in a price source and compute returns.")


if __name__ == "__main__":
    main()
