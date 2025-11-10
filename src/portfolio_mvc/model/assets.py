from dataclasses import dataclass, asdict
import pandas as pd
import os

@dataclass
class Asset:
    symbol: str
    sector: str
    asset_class: str
    quantity: float
    purchase_price: float

class AssetStore:
    CSV_COLUMNS = ["symbol", "sector", "asset_class", "quantity", "purchase_price"]

    def __init__(self, assets: list[Asset] | None = None):
        assets = assets or []
        self.df = pd.DataFrame([asdict(a) for a in assets], columns=self.CSV_COLUMNS)

    def add_asset(self, symbol: str, sector: str, asset_class: str, quantity: float, purchase_price: float) -> None:
            self.df.loc[len(self.df)] = {
                "symbol": symbol.upper(),
                "sector": sector,
                "asset_class": asset_class,
                "quantity": float(quantity),
                "purchase_price": float(purchase_price),
            }

    def remove_asset(self, symbol: str) -> bool:
        symbol = symbol.upper()
        if symbol in self.df["symbol"].values:
            self.df = self.df[self.df["symbol"] != symbol].reset_index(drop=True)
            return True
        return False

    def transaction_values(self) -> pd.Series:
        if self.df.empty:
            return pd.Series(dtype=float)
        return self.df["quantity"] * self.df["purchase_price"]

    def save_to_csv(self, filepath: str = "assets.csv") -> None:
        self.df.to_csv(filepath, index=False)

    def load_from_csv(self, filepath: str = "assets.csv") -> None:
        if os.path.exists(filepath):
            loaded = pd.read_csv(filepath)
            for col in self.CSV_COLUMNS:
                if col not in loaded.columns:
                    loaded[col] = pd.NA
            self.df = loaded[self.CSV_COLUMNS].copy()
        else:
            self.df = pd.DataFrame(columns=self.CSV_COLUMNS)
