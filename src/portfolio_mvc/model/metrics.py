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

def _periods_per_year(freq: Optional[str], interval: str) -> float:
    if freq:
        f = freq.upper()
        if f.startswith("Y"):
            return 1.0
        if f.startswith("M"):
            return 12.0
    if interval == "1wk":
        return 52.0
    if interval == "1mo":
        return 12.0
    return 252.0 

def _log_returns(series: pd.Series) -> pd.Series:
    series = series.dropna()
    if series.shape[0] < 2:
        return pd.Series(dtype="float64")
    return np.log(series / series.shift(1)).dropna()

def _annualized_metrics_from_log_returns(r: pd.Series, periods_per_year: float, rf: float = 0.0) -> dict:
    if r is None or r.empty:
        return {"ann_return": np.nan, "ann_vol": np.nan, "sharpe": np.nan}
    mu_log = r.mean()
    sig = r.std(ddof=1)
    ann_log_return = mu_log * periods_per_year
    ann_return = float(np.exp(ann_log_return) - 1.0)
    ann_vol = float(sig * np.sqrt(periods_per_year))
    if ann_vol == 0 or np.isnan(ann_vol):
        sharpe = np.nan
    else:
        sharpe = float((ann_return - rf) / ann_vol)
    return {"ann_return": ann_return, "ann_vol": ann_vol, "sharpe": sharpe}

def _max_drawdown(series: pd.Series) -> float:
    s = series.dropna().astype(float)
    if s.empty:
        return np.nan
    roll_max = s.cummax()
    dd = (s / roll_max) - 1.0
    return float(dd.min())

def benchmark_series(symbol: str, start: Optional[str], end: Optional[str], interval: str, freq: Optional[str]) -> pd.Series:
    hist = get_history([symbol], start=start, end=end, interval=interval)
    df = hist.get(symbol.upper(), pd.DataFrame())
    s = _pick_price_series(df)
    if s is None or s.empty:
        return pd.Series(dtype="float64")
    s = s.sort_index().dropna()
    if freq:
        f = freq.upper()
        rule = "ME" if f.startswith("M") else "YE"
        s = s.resample(rule).last().dropna()
    return s

def portfolio_metrics_from_series(series: pd.Series, periods_per_year: float, rf: float = 0.0) -> dict:
    r = _log_returns(series)
    stats = _annualized_metrics_from_log_returns(r, periods_per_year, rf=rf)
    mdd = _max_drawdown(series)
    out = {
        "start": series.index[0] if not series.empty else None,
        "end": series.index[-1] if not series.empty else None,
        "start_value": float(series.iloc[0]) if not series.empty else np.nan,
        "end_value": float(series.iloc[-1]) if not series.empty else np.nan,
        "total_return": float(series.iloc[-1] / series.iloc[0] - 1.0) if series.size >= 2 else np.nan,
        "max_drawdown": mdd,
    }
    out.update(stats)
    return out
