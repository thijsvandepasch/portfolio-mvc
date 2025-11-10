import pandas as pd
import pytest
from portfolio_mvc.model.assets import Asset, AssetStore


def test_add_asset():
    store = AssetStore()
    store.add_asset("AAPL", "Technology", "Equity", 10, 180)

    df = store.df
    assert "AAPL" in df["symbol"].values
    assert df.loc[0, "sector"] == "Technology"
    assert df.loc[0, "asset_class"] == "Equity"
    assert df.loc[0, "quantity"] == 10
    assert df.loc[0, "purchase_price"] == 180

    tx_value = float(df.loc[0, "quantity"]) * float(df.loc[0, "purchase_price"])
    assert tx_value == 10 * 180


def test_remove_asset():
    store = AssetStore()
    store.add_asset("TSLA", "Automotive", "Equity", 5, 200)
    removed = store.remove_asset("TSLA")

    assert removed is True
    assert "TSLA" not in store.df["symbol"].values


def test_remove_nonexistent_asset():
    store = AssetStore()
    removed = store.remove_asset("XYZ")
    assert removed is False


def test_weights_sum_to_one_using_purchase_values():
    store = AssetStore([
        Asset("AAPL", "Technology", "Equity", 10, 100),  # 1000
        Asset("MSFT", "Technology", "Equity", 10, 100),  # 1000
    ])
    df = store.df.copy()
    df["transaction_value"] = df["quantity"] * df["purchase_price"]
    total = df["transaction_value"].sum()
    df["weight"] = df["transaction_value"] / total if total > 0 else 0.0

    total_weight = round(df["weight"].sum(), 6)
    assert total_weight == 1.0


def test_save_and_load(tmp_path):
    test_file = tmp_path / "test_assets.csv"
    store = AssetStore()
    store.add_asset("NFLX", "Streaming", "Equity", 3, 450)
    store.save_to_csv(test_file)

    new_store = AssetStore()
    new_store.load_from_csv(test_file)

    df = new_store.df
    assert "NFLX" in df["symbol"].values
    assert df.loc[0, "quantity"] == 3
    assert df.loc[0, "purchase_price"] == 450

    tx_value = float(df.loc[0, "quantity"]) * float(df.loc[0, "purchase_price"])
    assert tx_value == 3 * 450
