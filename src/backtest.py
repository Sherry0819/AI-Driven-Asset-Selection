from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import pandas as pd
import numpy as np


def load_price_matrix_xlsx(path: str) -> pd.DataFrame:
    """Load a wide price matrix: rows=stocks, cols=dates."""
    df = pd.read_excel(path)
    # First column is stock identifier
    df = df.rename(columns={df.columns[0]: "stock"})
    df["stock"] = df["stock"].astype(str).str.strip()
    # date columns
    date_cols = [c for c in df.columns if c != "stock"]
    # Normalize datetime columns
    new_cols = {}
    for c in date_cols:
        try:
            new_cols[c] = pd.to_datetime(c).date()
        except Exception:
            new_cols[c] = c
    df = df.rename(columns=new_cols)
    return df


def portfolio_daily_returns(price_df: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    """Compute daily portfolio returns from a wide price matrix."""
    df = price_df.merge(weights, on="stock", how="inner").copy()
    date_cols = [c for c in df.columns if c not in ["stock", "weight"]]
    # sort date cols
    date_cols_sorted = sorted(date_cols)
    px = df[date_cols_sorted].astype(float)
    rets = px.pct_change(axis=1)  # daily returns across columns
    # weighted sum across stocks
    w = df["weight"].astype(float).values.reshape(-1, 1)
    port = (rets.values * w).sum(axis=0)
    out = pd.DataFrame({"date": date_cols_sorted, "portfolio_ret": port})
    out = out.dropna().reset_index(drop=True)
    out["portfolio_cum"] = (1 + out["portfolio_ret"]).cumprod() - 1
    return out
