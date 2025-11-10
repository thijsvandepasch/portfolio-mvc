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
    if combine:
        any_plotted = False
        plt.figure()
        for sym, df in history.items():
            if not df.empty:
                df["Close"].plot(label=sym)
                any_plotted = True
        if not any_plotted:
            return
        plt.legend()
        plt.title("Historical Prices")
        plt.xlabel("Date")
        plt.ylabel("Close")
        plt.show()
    else:
        for sym, df in history.items():
            if isinstance(df, pd.DataFrame) and not df.empty and "Close" in df:
                plt.figure()
                df["Close"].plot()
                plt.title(f"{sym} - Historical Prices")
                plt.xlabel("Date")
                plt.ylabel("Close")
                plt.show()
