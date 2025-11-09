from portfolio_mvc.model.assets import AssetStore
from portfolio_mvc.view.tables import print_assets
from portfolio_mvc.view.charts import plot_weights
from portfolio_mvc.view.cli import run_cli
import os

# Initialize store and load previous data
_store = AssetStore()
_store.load_from_csv()

def handle_command(cmd: str, payload: dict):
    """
    Interpret commands and manage data flow between Model and View.
    """
    if cmd == "add":
        _store.add_asset(payload["symbol"], float(payload["value"]))
        _store.save_to_csv()
        df = _store.weights()
        print_assets(df)

    elif cmd == "show":
        df = _store.weights()
        print_assets(df)
        if payload.get("plot"):
            plot_weights(df)

    elif cmd == "reset":
        if os.path.exists("assets.csv"):
            os.remove("assets.csv")
        _store.df = _store.df.iloc[0:0]
        print("✅ Portfolio reset successfully. (assets.csv deleted)")

    elif cmd == "remove":
        symbol = payload["symbol"]
        removed = _store.remove_asset(symbol)
        if removed:
            _store.save_to_csv()
            df = _store.weights()
            print(f"✅ Removed {symbol} from portfolio.")
            print_assets(df)
        else:
            print(f"⚠️ No asset found with symbol '{symbol}'.")

    else:
        print("Unknown command:", cmd)

def main():
    run_cli(handle_command)

if __name__ == "__main__":
    main()
