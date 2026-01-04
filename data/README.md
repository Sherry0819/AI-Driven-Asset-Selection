# Data

## Sample data (included)
`data/sample/` contains small files so you can run the project immediately:

- `merged_news_clean.xlsx` — headlines + timestamps
- `price_matrix.xlsx` — a small panel of prices for a subset of S&P 500 stocks

## Raw data (local only)
Put larger inputs or licensed datasets under:

```
data/raw/
```

This directory is **git-ignored** by default.

## API keys (never commit)
If you use NewsAPI, export an environment variable:

```bash
export NEWSAPI_KEY="YOUR_KEY"
```
