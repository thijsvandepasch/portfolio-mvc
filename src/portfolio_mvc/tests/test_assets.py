import pandas as pd
from portfolio_mvc.model.assets import Asset, AssetStore

def test_add_asset():
    store = AssetStore()
    store.add_asset("AAPL", 1000)

    df = store.df
    assert "AAPL" in df["symbol"].values
    assert df.loc[0, "value"] == 1000.0

def test_remove_asset():
    store = AssetStore()
    store.add_asset("TSLA", 1500)
    removed = store.remove_asset("TSLA")

    # Asset should be removed
    assert removed is True
    assert "TSLA" not in store.df["symbol"].values

def test_remove_nonexistent_asset():
    store = AssetStore()
    removed = store.remove_asset("XYZ")
    assert removed is False

def test_weights_sum_to_one():
    store = AssetStore([
        Asset("AAPL", 50),
        Asset("MSFT", 50)
    ])
    df = store.weights()
    total_weight = round(df["weight"].sum(), 6)
    assert total_weight == 1.0

def test_save_and_load(tmp_path):
    """
    tmp_path is a pytest fixture that gives you a temporary folder to test with.
    """
    test_file = tmp_path / "test_assets.csv"
    store = AssetStore()
    store.add_asset("NFLX", 2500)
    store.save_to_csv(test_file)

    # Load into a new store instance
    new_store = AssetStore()
    new_store.load_from_csv(test_file)

    assert "NFLX" in new_store.df["symbol"].values
    assert new_store.df.loc[0, "value"] == 2500.0
