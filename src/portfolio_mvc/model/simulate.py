import numpy as np
import pandas as pd
from portfolio_mvc.model.pricing import get_history

def _pick_price(df: pd.DataFrame) -> pd.Series | None:
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

def _returns_from_history(history: dict[str, pd.DataFrame], freq: str) -> pd.DataFrame:
    f = freq.upper()
    if f.startswith("A"):
        rule = "YE"
    elif f.startswith("M"):
        rule = "ME"
    else:
        rule = "YE"
    frames = []
    for sym, df in history.items():
        px = _pick_price(df)
        if px is None or px.shape[0] < 3:
            continue
        r_daily = np.log(px / px.shift(1)).dropna()
        if r_daily.empty:
            continue
        r_period = r_daily.resample(rule).sum().dropna()
        if r_period.shape[0] < 1:
            continue
        frames.append(pd.DataFrame({sym: r_period}))
    if not frames:
        return pd.DataFrame()
    R = pd.concat(frames, axis=1).sort_index()
    R = R.dropna(how="all")
    return R

def simulate_portfolio_paths(
    df_positions: pd.DataFrame,
    years: int = 15,
    paths: int = 100_000,
    freq: str = "YE",
) -> dict:
    if df_positions.empty:
        return {"error": "No positions to simulate."}
    f = freq.upper()
    if f.startswith("A"):
        f = "YE"
    elif f.startswith("M"):
        f = "ME"
    else:
        f = "YE"
    symbols = [s.upper() for s in df_positions["symbol"].tolist()]

    hist = get_history(symbols, start=None, end=None, interval="1d")
    R = _returns_from_history(hist, freq=f)
    min_steps = 2 if f == "YE" else 3
    if R.empty or R.shape[0] < min_steps:
        hist = get_history(symbols, start="2018-01-01", end=None, interval="1d")
        R = _returns_from_history(hist, freq=f)
    if R.empty or R.shape[0] < min_steps:
        hist = get_history(symbols, start="2015-01-01", end=None, interval="1d")
        R = _returns_from_history(hist, freq=f)
    if R.empty or R.shape[0] < min_steps:
        return {"error": "Insufficient history to estimate returns."}

    mu_by_col = R.mean(skipna=True)
    cov_by_col = R.cov()
    kept_symbols = [c for c in mu_by_col.index if c in cov_by_col.index]
    if not kept_symbols:
        return {"error": "Insufficient history to estimate returns."}

    last_prices = []
    final_symbols = []
    for s in kept_symbols:
        dfh = hist.get(s, pd.DataFrame())
        px = _pick_price(dfh)
        if px is None or px.empty:
            continue
        last_prices.append(float(px.iloc[-1]))
        final_symbols.append(s)
    if not final_symbols:
        return {"error": "Insufficient history to estimate returns."}

    qty = (
        df_positions.set_index("symbol")
        .reindex(final_symbols)["quantity"]
        .astype(float)
        .to_numpy()
    )
    mu_vec = mu_by_col.reindex(final_symbols).to_numpy()
    cov_mat = cov_by_col.reindex(index=final_symbols, columns=final_symbols).to_numpy()

    n_assets = len(final_symbols)
    steps = years if f == "YE" else years * 12

    if n_assets == 1:
        rng = np.random.default_rng()
        z = rng.standard_normal(size=(paths, steps))
        vol = float(np.sqrt(cov_mat[0, 0])) if cov_mat.size else 0.0
        rets = mu_vec[0] + vol * z
        log_cum = np.cumsum(rets, axis=1)
        p0 = float(last_prices[0])
        prices_paths = p0 * np.exp(log_cum)
        price_T = prices_paths[:, -1]
        port_T = price_T * qty[0]
    else:
        n = cov_mat.shape[0]
        jitter = 1e-12
        for _ in range(8):
            try:
                L = np.linalg.cholesky(cov_mat + jitter * np.eye(n))
                break
            except np.linalg.LinAlgError:
                jitter *= 10
        rng = np.random.default_rng()
        Z = rng.standard_normal(size=(paths, steps, n_assets))
        cor_Z = Z @ L
        rets = mu_vec.reshape((1, 1, n_assets)) + cor_Z
        log_cum = np.cumsum(rets, axis=1)
        last_prices = np.asarray(last_prices, dtype=float)
        prices_paths = last_prices.reshape((1, 1, n_assets)) * np.exp(log_cum)
        price_T = prices_paths[:, -1, :]
        port_T = (price_T * qty.reshape((1, n_assets))).sum(axis=1)

    summary = {
        "paths": paths,
        "years": years,
        "freq": f,
        "mean_ending_value": float(port_T.mean()),
        "median_ending_value": float(np.median(port_T)),
        "p5": float(np.percentile(port_T, 5)),
        "p25": float(np.percentile(port_T, 25)),
        "p75": float(np.percentile(port_T, 75)),
        "p95": float(np.percentile(port_T, 95)),
    }
    return {"summary": summary, "samples": port_T}
