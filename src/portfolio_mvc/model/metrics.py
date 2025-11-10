import pandas as pd
import numpy as np
from portfolio_mvc.model.pricing import get_current_prices

def with_current_values(df_assets: pd.DataFrame) -> pd.DataFrame:
    if df_assets.empty:
        cols = ["symbol","sector","asset_class","quantity","purchase_price","transaction_value","current_price","current_value"]
        return pd.DataFrame(columns=cols)

    df = df_assets.copy()
    df["transaction_value"] = df["quantity"] * df["purchase_price"]

    cur = get_current_prices(df["symbol"].tolist())
    df = df.merge(cur.rename("current_price"), left_on="symbol", right_index=True, how="left")
    df["current_value"] = df["quantity"] * df["current_price"]
    return df

def total_and_weights(df_values: pd.DataFrame) -> tuple[float, pd.DataFrame]:
    if df_values.empty:
        return 0.0, df_values.assign(weight=np.nan)
    total = float(df_values["current_value"].sum(skipna=True))
    df = df_values.copy()
    df["weight"] = df["current_value"] / total if total > 0 else np.nan
    return total, df

def grouped_weights(df_values: pd.DataFrame, by: str) -> pd.DataFrame:
    assert by in ("sector", "asset_class")
    if df_values.empty:
        return pd.DataFrame(columns=[by, "current_value", "weight"])
    grp = df_values.groupby(by, dropna=False)["current_value"].sum().reset_index()
    total = float(grp["current_value"].sum())
    grp["weight"] = grp["current_value"] / total if total > 0 else np.nan
    return grp
