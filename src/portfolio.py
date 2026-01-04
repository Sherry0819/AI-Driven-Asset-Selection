from __future__ import annotations

import pandas as pd
import numpy as np
from typing import List, Dict


def normalize_weights(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize so sum(abs(w))=1."""
    w = df["weight"].astype(float)
    s = w.abs().sum()
    if s == 0 or np.isnan(s):
        raise ValueError("Weights sum to zero.")
    df["weight"] = w / s
    return df


def portfolio_from_llm_output(arr: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(arr)
    if "stock" not in df.columns or "weight" not in df.columns:
        raise ValueError("Expected fields: stock, weight")
    df["stock"] = df["stock"].astype(str).str.strip()
    df = df.dropna(subset=["stock", "weight"]).copy()
    df = normalize_weights(df)
    return df
