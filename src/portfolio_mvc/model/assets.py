from dataclasses import dataclass
import pandas as pd
import os

@dataclass
class Asset:
    symbol: str
    value: float

class AssetStore:
    """
    Holds asset data, computes weights, and saves/loads to disk.
    """
    def __init__(self, assets: list[Asset] | None = None):
        assets = assets or []
        self.df = pd.DataFrame([a.__dict__ for a in assets], columns=["symbol", "value"])

    def add_asset(self, symbol: str, value: float) -> None:
        """
        Add a new asset to the portfolio.
        """
        self.df.loc[len(self.df)] = {"symbol": symbol, "value": float(value)}

    def weights(self) -> pd.DataFrame:
        """
        Calculate weights for all assets (value / total).
        """
        total = float(self.df["value"].sum()) if len(self.df) else 0.0
        self.df["weight"] = (self.df["value"] / total) if total else 0.0
        return self.df[["symbol", "value", "weight"]].copy()

    # --- Persistence ---
    def save_to_csv(self, filepath: str = "assets.csv") -> None:
        """
        Save portfolio to CSV file.
        """
        self.df.to_csv(filepath, index=False)

    def load_from_csv(self, filepath: str = "assets.csv") -> None:
        """
        Load portfolio from CSV if it exists.
        """
        if os.path.exists(filepath):
            self.df = pd.read_csv(filepath)
        else:
            self.df = pd.DataFrame(columns=["symbol", "value"])

    def remove_asset(self, symbol: str) -> bool:
        """
        Remove an asset by its symbol.
        Returns True if removed, False if symbol not found.
        """
        if symbol in self.df["symbol"].values:
            self.df = self.df[self.df["symbol"] != symbol].reset_index(drop=True)
            return True
        else:
            return False
