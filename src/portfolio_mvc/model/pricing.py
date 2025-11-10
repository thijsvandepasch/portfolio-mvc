from __future__ import annotations
import pandas as pd
import yfinance as yf
from typing import Iterable

def get_current_price(symbol: str) -> float | None:
    symbol = symbol.upper()
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info if hasattr(ticker, "fast_info") else None
        if info and "last_price" in info.__dict__.get("dict", {}) or hasattr(info, "last_price"):
            return float(getattr(info, "last_price"))
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
        try:
            df = yf.download(sym, start=start, end=end, interval=interval, auto_adjust=False, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df = df.droplevel(0, axis=1)
            out[sym.upper()] = df
        except Exception:
            out[sym.upper()] = pd.DataFrame()
    return out
