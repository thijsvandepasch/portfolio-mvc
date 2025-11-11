import pandas as pd
import numpy as np
from portfolio_mvc.model.pricing import get_current_prices
from typing import Optional, Dict
from portfolio_mvc.model.pricing import get_history

def with_current_values(df_assets: pd.DataFrame) -> pd.DataFrame:
    if df_assets.empty:
        cols = ["symbol","sector","asset_class","quantity","purchase_price","transaction_value","current_price","current_value"]
        return pd.DataFrame(columns=cols)

    df = df_assets.copy()
    df["transaction_value"] = df["quantity"] * df["purchase_price"]

    cur = get_current_prices(df["symbol"].tolist())
    df = df.merge(cur.rename("current_price"), left_on="symbol", right_index=True, how="left")
    df["current_value"] = df["quantity"] * df["current_price"]
    return df

def total_and_weights(df_values: pd.DataFrame) -> tuple[float, pd.DataFrame]:
    if df_values.empty:
        return 0.0, df_values.assign(weight=np.nan)
    total = float(df_values["current_value"].sum(skipna=True))
    df = df_values.copy()
    df["weight"] = df["current_value"] / total if total > 0 else np.nan
    return total, df

def grouped_weights(df_values: pd.DataFrame, by: str) -> pd.DataFrame:
    assert by in ("sector", "asset_class")
    if df_values.empty:
        return pd.DataFrame(columns=[by, "current_value", "weight"])
    grp = df_values.groupby(by, dropna=False)["current_value"].sum().reset_index()
    total = float(grp["current_value"].sum())
    grp["weight"] = grp["current_value"] / total if total > 0 else np.nan
    return grp

def _pick_price_series(df: pd.DataFrame) -> Optional[pd.Series]:
    if df is None or df.empty:
        return None
    if "Close" in df.columns:
        s = df["Close"].dropna()
        return s if not s.empty else None
    if "Adj Close" in df.columns:
        s = df["Adj Close"].dropna()
        return s if not s.empty else None
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not num_cols:
        return None
    s = df[num_cols[-1]].dropna()
    return s if not s.empty else None

def portfolio_value_series(
    df_positions: pd.DataFrame,
    start: Optional[str] = None,
    end: Optional[str] = None,
    interval: str = "1d",
    freq: Optional[str] = None,
) -> pd.Series:
    if df_positions is None or df_positions.empty:
        return pd.Series(dtype="float64")

    syms = [s.upper() for s in df_positions["symbol"].astype(str).tolist()]
    qty_by_sym = (
        df_positions.assign(symbol=lambda d: d["symbol"].str.upper())
        .groupby("symbol")["quantity"]
        .sum()
    )

    hist: Dict[str, pd.DataFrame] = get_history(syms, start=start, end=end, interval=interval)

    price_cols = {}
    for sym, df in hist.items():
        s = _pick_price_series(df)
        if s is not None:
            price_cols[sym] = s

    if not price_cols:
        return pd.Series(dtype="float64")

    prices = pd.concat(price_cols, axis=1)
    prices = prices.sort_index()

    qty = qty_by_sym.reindex(prices.columns).fillna(0.0)

    values = (prices * qty).sum(axis=1)

    if freq:
        f = freq.upper()
        rule = "ME" if f.startswith("M") else "YE"
        values = values.resample(rule).last().dropna()

    return values.dropna()
