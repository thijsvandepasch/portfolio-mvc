import matplotlib.pyplot as plt
import pandas as pd

def plot_weights(df: pd.DataFrame) -> None:
    """
    Simple pie chart of weights.
    (One figure, default colors, no custom style.)
    """
    if df.empty or "weight" not in df:
        return
    plt.figure()
    plt.pie(df["weight"], labels=df["symbol"], autopct="%1.1f%%")
    plt.title("Portfolio Weights")
    plt.show()