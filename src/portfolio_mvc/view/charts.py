import matplotlib.pyplot as plt
import pandas as pd

def plot_weights(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        return
    if "weight" not in df.columns or "symbol" not in df.columns:
        return
    data = df.dropna(subset=["weight"])
    if data.empty:
        return
    plt.figure()
    plt.pie(data["weight"], labels=data["symbol"], autopct="%1.1f%%")
    plt.title("Portfolio Weights")
    plt.show()

def plot_price_series(history: dict[str, pd.DataFrame], combine: bool = True) -> None:
    if not history:
        return

    def pick_close(df: pd.DataFrame):
        if df is None or df.empty:
            return None
        if "Close" in df.columns:
            s = df["Close"].dropna()
            return s if not s.empty else None
        if "Adj Close" in df.columns:
            s = df["Adj Close"].dropna()
            return s if not s.empty else None
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if num_cols:
            s = df[num_cols[-1]].dropna()
            return s if not s.empty else None
        return None

    if combine:
        plt.figure()
        any_plotted = False
        for sym, df in history.items():
            s = pick_close(df)
            if s is not None:
                s.plot(label=sym)
                any_plotted = True
        if any_plotted:
            plt.legend()
            plt.title("Historical Prices")
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.show()
        return

    for sym, df in history.items():
        s = pick_close(df)
        if s is None:
            continue
        plt.figure()
        s.plot()
        plt.title(f"{sym} - Historical Prices")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.show()

def plot_portfolio_series(series: pd.Series, title: str = "Portfolio Value Over Time") -> None:
    if series is None or series.empty:
        return
    plt.figure()
    series.plot()
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.show()
