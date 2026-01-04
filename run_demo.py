from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from src.news import load_news_xlsx, build_news_window
from src.llm import OllamaClient, safe_load_json_array
from src.portfolio import portfolio_from_llm_output
from src.backtest import load_price_matrix_xlsx, portfolio_daily_returns

import matplotlib.pyplot as plt


def main():
    news_path = "data/sample/merged_news_clean.xlsx"
    price_path = "data/sample/price_matrix.xlsx"
    outdir = Path("reports")
    (outdir / "figures").mkdir(parents=True, exist_ok=True)

    # 1) Load sample news and build a rolling window (last 7 days as of formation)
    df_news = load_news_xlsx(news_path)
    asof = df_news["Date"].max()  # use latest timestamp in the sample
    headlines = build_news_window(df_news, asof=asof, lookback_days=7)

    # 2) Select portfolio using Ollama (local). If you don't have Ollama running,
    # replace this block with a manual JSON portfolio for testing.
    client = OllamaClient(model="gemma2")
    raw = client.select_portfolio(headlines_bullets=headlines, universe_hint="S&P 500", n=20)
    w = portfolio_from_llm_output(raw)

    # 3) Backtest on the included price matrix (demo horizon)
    px = load_price_matrix_xlsx(price_path)
    daily = portfolio_daily_returns(px, w)

    # Save artifacts
    w.to_csv(outdir / "demo_portfolio.csv", index=False)
    daily.to_csv(outdir / "demo_daily_returns.csv", index=False)

    # Plot cumulative
    plt.figure()
    plt.plot(pd.to_datetime(daily["date"]), daily["portfolio_cum"])
    plt.axhline(0, linewidth=0.8)
    plt.title("Demo: Portfolio Cumulative Return")
    plt.xlabel("Date")
    plt.ylabel("Cumulative return")
    plt.tight_layout()
    plt.savefig(outdir / "figures" / "demo_cumulative.png", dpi=200)
    plt.close()

    print("Done. See reports/ for outputs.")


if __name__ == "__main__":
    main()
