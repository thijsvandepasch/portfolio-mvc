import numpy as np
import pandas as pd
from portfolio_mvc.model.pricing import get_history

def _returns_from_history(history: dict[str, pd.DataFrame], freq: str) -> pd.DataFrame:
    frames = []
    for sym, df in history.items():
        if df.empty: 
            continue
        prices = df["Close"].dropna().copy()
        rule = "A" if freq.upper().startswith("A") else "M"
        px = prices.resample(rule).last().dropna()
        rets = np.log(px / px.shift(1)).dropna()
        frames.append(pd.DataFrame({sym: rets}))
    if not frames:
        return pd.DataFrame()
    R = pd.concat(frames, axis=1).dropna(how="any")
    return R

def simulate_portfolio_paths(
    df_positions: pd.DataFrame,
    years: int = 15,
    paths: int = 100_000,
    freq: str = "A",
) -> dict:
    if df_positions.empty:
        return {"error": "No positions to simulate."}

    symbols = df_positions["symbol"].tolist()

    hist = get_history(symbols, start=None, end=None, interval="1d")
    R = _returns_from_history(hist, freq=freq)
    if R.empty:
        return {"error": "Insufficient history to estimate returns."}

    mu = R.mean().values
    cov = R.cov().values
    n_assets = len(mu)

    last_prices = []
    for s in symbols:
        df = hist.get(s.upper(), pd.DataFrame())
        if df.empty: 
            last_prices.append(np.nan)
        else:
            last_prices.append(float(df["Close"].dropna().iloc[-1]))
    last_prices = np.array(last_prices, dtype=float)

    qty = df_positions["quantity"].to_numpy(dtype=float)

    steps = years if freq.upper().startswith("A") else years * 12

    rng = np.random.default_rng()
    L = np.linalg.cholesky(cov + 1e-12*np.eye(n_assets))
    Z = rng.standard_normal(size=(paths, steps, n_assets))
    cor_Z = Z @ L

    rets = mu.reshape((1,1,n_assets)) + cor_Z

    log_cum = np.cumsum(rets, axis=1)
    prices_paths = last_prices.reshape((1,1,n_assets)) * np.exp(log_cum)

    price_T = prices_paths[:, -1, :]
    port_T = (price_T * qty.reshape((1, n_assets))).sum(axis=1)

    summary = {
        "paths": paths,
        "years": years,
        "freq": freq,
        "mean_ending_value": float(port_T.mean()),
        "median_ending_value": float(np.median(port_T)),
        "p5": float(np.percentile(port_T, 5)),
        "p25": float(np.percentile(port_T, 25)),
        "p75": float(np.percentile(port_T, 75)),
        "p95": float(np.percentile(port_T, 95)),
    }
    return {"summary": summary, "samples": port_T}
