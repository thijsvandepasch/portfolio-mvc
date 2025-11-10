from portfolio_mvc.model.assets import AssetStore
from portfolio_mvc.model.metrics import with_current_values, total_and_weights, grouped_weights
from portfolio_mvc.model.pricing import get_history, get_current_prices
from portfolio_mvc.model.simulate import simulate_portfolio_paths
from portfolio_mvc.view.tables import print_assets_full, print_grouped, print_total
from portfolio_mvc.view.charts import plot_weights, plot_price_series
from portfolio_mvc.view.cli import run_cli
import os

_store = AssetStore()
_store.load_from_csv()

def handle_command(cmd: str, payload: dict):
    if cmd == "add":
        _store.add_asset(
            payload["symbol"], payload["sector"], payload["asset_class"],
            float(payload["quantity"]), float(payload["purchase_price"])
        )
        _store.save_to_csv()
        dfv = with_current_values(_store.df)
        _, dfw = total_and_weights(dfv)
        print_assets_full(dfw)

    elif cmd == "remove":
        symbol = payload["symbol"]
        removed = _store.remove_asset(symbol)
        if removed:
            _store.save_to_csv()
            print(f"✅ Removed {symbol.upper()}.")
        else:
            print(f"⚠️ No asset with symbol '{symbol}'.")
        dfv = with_current_values(_store.df)
        _, dfw = total_and_weights(dfv)
        print_assets_full(dfw)

    elif cmd == "show":
        dfv = with_current_values(_store.df)
        total, dfw = total_and_weights(dfv)
        print_assets_full(dfw)
        print_total(total)
        grp = payload.get("group")
        if grp in ("sector", "asset_class"):
            g = grouped_weights(dfv, by=grp)
            title = f"Weights by {grp}"
            print_grouped(g, title)
        if payload.get("plot"):
            plot_weights(dfw.dropna(subset=["weight"]))

    elif cmd == "prices":
        symbols = payload["symbols"]
        start, end, interval = payload.get("start"), payload.get("end"), payload.get("interval", "1d")
        combine = bool(payload.get("combine", True))
        cur = get_current_prices(symbols)
        print("Current prices:")
        for sym, px in cur.items():
            print(f"  {sym}: {px:.4f}" if px == px else f"  {sym}: N/A")
        hist = get_history(symbols, start=start, end=end, interval=interval)
        plot_price_series(hist, combine=combine)

    elif cmd == "simulate":
        years = int(payload.get("years", 15))
        paths = int(payload.get("paths", 100_000))
        freq  = payload.get("freq", "A")
        res = simulate_portfolio_paths(_store.df, years=years, paths=paths, freq=freq)
        if "error" in res:
            print("⚠️", res["error"])
            return
        summary = res["summary"]
        print("Simulation summary (ending portfolio value):")
        for k in ["mean_ending_value","median_ending_value","p5","p25","p75","p95"]:
            print(f"  {k}: {summary[k]:,.2f}")
        if payload.get("plot") and "samples" in res:
            try:
                import matplotlib.pyplot as plt
                import numpy as np
                plt.figure()
                plt.hist(res["samples"], bins=60)
                plt.title(f"Ending Value Distribution ({paths} paths, {years}y, {freq})")
                plt.xlabel("Ending value")
                plt.ylabel("Frequency")
                plt.show()
            except Exception:
                pass

    else:
        print("Unknown command:", cmd)

def main():
    run_cli(handle_command)

if __name__ == "__main__":
    main()
