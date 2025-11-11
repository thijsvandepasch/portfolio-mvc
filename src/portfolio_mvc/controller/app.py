from portfolio_mvc.model.assets import AssetStore
from portfolio_mvc.model.metrics import with_current_values, total_and_weights, grouped_weights
from portfolio_mvc.model.pricing import get_history, get_current_prices
from portfolio_mvc.model.simulate import simulate_portfolio_paths
from portfolio_mvc.view.tables import print_assets_full, print_grouped, print_total
from portfolio_mvc.view.charts import plot_weights, plot_price_series
from portfolio_mvc.view.cli import run_cli
from portfolio_mvc.model.metrics import portfolio_value_series
from portfolio_mvc.view.charts import plot_portfolio_series
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

    elif cmd == "reset":
        confirm = input("⚠️ Are you sure you want to delete all portfolio data? (y/n): ")
        if confirm.lower().startswith("y"):
            _store.df = _store.df.iloc[0:0]
            if os.path.exists("assets.csv"):
                os.remove("assets.csv")
            print("✅ Portfolio has been reset.")
        else:
            print("❌ Reset cancelled.")

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
                plt.hist(res["samples"], bins=60, range=(0, 1_000_000))
                plt.title(f"Ending Value Distribution ({paths} paths, {years}y, {freq})")
                plt.xlabel("Ending value")
                plt.ylabel("Frequency")
                plt.ticklabel_format(style='plain', axis='x')
                plt.show()
            except Exception:
                pass

    elif cmd == "performance":
        start = payload.get("start")
        end = payload.get("end")
        interval = payload.get("interval", "1d")
        freq = payload.get("freq")
        do_plot = bool(payload.get("plot", True))

        if _store.df.empty:
            print("No assets in portfolio.")
            return

        series = portfolio_value_series(_store.df, start=start, end=end, interval=interval, freq=freq)
        if series.empty:
            print("No historical data available for current holdings and date range.")
            return

        start_dt, end_dt = series.index[0].date(), series.index[-1].date()
        v0, vT = float(series.iloc[0]), float(series.iloc[-1])
        ret = (vT / v0 - 1.0) if v0 != 0 else float("nan")
        print(f"Period: {start_dt} → {end_dt}")
        print(f"Start value: {v0:,.2f}")
        print(f"End value:   {vT:,.2f}")
        print(f"Return:      {ret*100:,.2f}%")

        if do_plot:
            ttl = f"Portfolio Value Over Time ({freq or 'daily'})"
            plot_portfolio_series(series, title=ttl)

        else:
            print("Unknown command:", cmd)

def main():
    run_cli(handle_command)

if __name__ == "__main__":
    main()
