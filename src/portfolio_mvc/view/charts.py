import matplotlib.pyplot as plt
import pandas as pd

def plot_price_series(history: dict[str, pd.DataFrame], combine: bool = True) -> None:
    if not history:
        return
    if combine:
        plt.figure()
        for sym, df in history.items():
            if not df.empty:
                df["Close"].plot(label=sym)
        plt.legend()
        plt.title("Historical Prices")
        plt.xlabel("Date")
        plt.ylabel("Close")
        plt.show()
    else:
        for sym, df in history.items():
            if df.empty:
                continue
            plt.figure()
            df["Close"].plot()
            plt.title(f"{sym} - Historical Prices")
            plt.xlabel("Date")
            plt.ylabel("Close")
            plt.show()
            