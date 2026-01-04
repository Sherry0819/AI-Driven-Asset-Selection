# AI‑Driven Stock Selection from News: LLM Signal + Backtesting

This repository explores a practical workflow for **using financial news to generate an investable signal** and evaluating it via a transparent backtest.

The core idea is simple:

1. **Collect headlines** for a chosen universe (e.g., S&P 500).
2. Convert news into a **daily/weekly "score" or ranking** (via LLM or sentiment model).
3. Build a **long/short portfolio** based on that signal.
4. **Backtest** with realistic rebalancing and clear benchmarks.

## What’s improved vs a one‑off demo

- Uses **more news** by design (rolling window of headlines per rebalance date).
- Supports **repeated rebalancing** (daily/weekly) rather than a single formation date.
- Clean separation between:
  - news ingestion
  - LLM prompting / sentiment scoring
  - portfolio construction
  - backtesting + benchmarking

## Quickstart (sample run with included data)

This repo ships with small sample inputs under `data/sample/`:
- `merged_news_clean.xlsx` (headlines + timestamps)
- `price_matrix.xlsx` (a small price panel)

Run the demo backtest:

```bash
python run_demo.py
```

Outputs:
- `reports/demo_portfolio.csv`
- `reports/demo_daily_returns.csv`
- `reports/figures/demo_cumulative.png`

## Full pipeline (optional, needs API keys / internet)

- **NewsAPI** fetcher: set `NEWSAPI_KEY` (environment variable)
- **LLM selector**:
  - Ollama (local) *or* OpenAI API (optional adapter)

See `run_backtest.py --help`.

> This repo does **not** require you to push API keys or private datasets. Put any larger/raw inputs in `data/raw/` (git‑ignored).

## Repository layout

- `src/news.py` — load/fetch headlines, build rolling windows
- `src/llm.py` — LLM adapters + safe JSON parsing
- `src/portfolio.py` — convert scores/selections to weights
- `src/backtest.py` — portfolio returns, rebalancing, benchmarks
- `run_demo.py` — reproducible demo using included sample files
- `run_backtest.py` — full pipeline runner (NewsAPI + prices)

## Notes / Ideas to extend

- Use a **ticker‑matching step** (NER + company → ticker)
- Replace LLM selection with **FinBERT / LM dictionary** sentiment
- Add transaction costs, slippage, and exposure constraints
