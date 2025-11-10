from __future__ import annotations
import pandas as pd
import yfinance as yf
from typing import Iterable

def _standardize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df = df.copy()
            df.index = pd.to_datetime(df.index)
        except Exception:
            pass

    if isinstance(df.columns, pd.MultiIndex):
        fields = {"Open","High","Low","Close","Adj Close","Volume"}
        level_has_fields = [
            any(val in fields for val in df.columns.get_level_values(i))
            for i in range(df.columns.nlevels)
        ]
        if any(level_has_fields):
            keep_level = level_has_fields.index(True)
            drop_level = 1 - keep_level if df.columns.nlevels == 2 else None
            if drop_level is not None:
                df = df.droplevel(drop_level, axis=1)

    std_fields = ["Open","High","Low","Close","Adj Close","Volume"]
    have_close = "Close" in df.columns

    if not have_close:
        if df.columns.name and df.columns.name.lower() == "ticker":
            if df.shape[1] >= 6:
                df = df.copy()
                df.columns = std_fields[:df.shape[1]]
            elif df.shape[1] == 5:
                df = df.copy()
                df.columns = ["Open","High","Low","Close","Volume"]
        if "Close" not in df.columns:
            if df.shape[1] >= 6:
                df = df.copy()
                df.columns = std_fields[:df.shape[1]]
            elif df.shape[1] == 5:
                cols = list(df.columns)
                df = df.copy()
                if "Close" not in cols:
                    df.columns = ["Open","High","Low","Close","Volume"]

    keep = [c for c in std_fields if c in df.columns]
    return df[keep].copy() if keep else df.copy()

def get_current_price(symbol: str) -> float | None:
    symbol = symbol.upper()
    try:
        ticker = yf.Ticker(symbol)
        fi = getattr(ticker, "fast_info", None)
        if fi is not None:
            lp = getattr(fi, "last_price", None)
            if lp is not None:
                return float(lp)
        hist = ticker.history(period="5d")
        if not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])
    except Exception:
        pass
    return None

def get_current_prices(symbols: Iterable[str]) -> pd.Series:
    prices = {}
    for s in symbols:
        price = get_current_price(s)
        prices[s.upper()] = float(price) if price is not None else float("nan")
    return pd.Series(prices, name="price")

def get_history(
    symbols: list[str],
    start: str | None = None,
    end: str | None = None,
    interval: str = "1d",
) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for sym in symbols:
        s = sym.upper()
        try:
            df = yf.download(
                s, start=start, end=end, interval=interval,
                auto_adjust=False, progress=False, group_by="column"
            )
            df = _standardize_ohlcv(df)
            out[s] = df
        except Exception:
            out[s] = pd.DataFrame()
    return out
