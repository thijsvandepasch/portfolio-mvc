import typer
from typing import Optional, List

app = typer.Typer(help="Portfolio Management CLI")

def run_cli(controller_callback):

    @app.command("add")
    def add(
        symbol: str,
        sector: str,
        asset_class: str,
        quantity: float,
        purchase_price: float,
    ):
        controller_callback("add", {
            "symbol": symbol,
            "sector": sector,
            "asset_class": asset_class,
            "quantity": quantity,
            "purchase_price": purchase_price
        })

    @app.command("remove")
    def remove(symbol: str):
        controller_callback("remove", {"symbol": symbol})

    @app.command("show")
    def show(
        group: Optional[str] = typer.Option(None, help="None | sector | asset_class"),
        plot: bool = typer.Option(False, help="Also show a pie chart of weights"),
    ):
        controller_callback("show", {"group": group, "plot": plot})

    @app.command("prices")
    def prices(
        symbols: List[str] = typer.Argument(..., help="One or more tickers"),
        start: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
        end: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
        interval: str = typer.Option("1d", help="1d|1wk|1mo"),
        combine: bool = typer.Option(True, "--combine/--no-combine", help="Plot on one chart"),
    ):
        controller_callback("prices", {
            "symbols": symbols, "start": start, "end": end, "interval": interval, "combine": combine
        })

    @app.command("simulate")
    def simulate(
        years: int = typer.Option(15, help="Horizon in years"),
        paths: int = typer.Option(100_000, help="Number of Monte Carlo paths"),
        freq: str = typer.Option("A", help="Time step: A=annual, M=monthly"),
        plot: bool = typer.Option(True, help="Plot ending value distribution"),
    ):
        controller_callback("simulate", {"years": years, "paths": paths, "freq": freq, "plot": plot})

    @app.command("reset")
    def reset():
        controller_callback("reset", {})

    @app.command("performance")
    def performance(
        start: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
        end: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
        interval: str = typer.Option("1d", help="1d|1wk|1mo"),
        freq: Optional[str] = typer.Option(None, help="ME (month-end) or YE (year-end)"),
        plot: bool = typer.Option(True, help="Show a chart of total portfolio value"),
    ):
        controller_callback(
            "performance",
            {"start": start, "end": end, "interval": interval, "freq": freq, "plot": plot},
        )

    @app.command("metrics")
    def metrics(
        start: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
        end: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
        interval: str = typer.Option("1d", help="1d|1wk|1mo"),
        freq: Optional[str] = typer.Option("ME", help="ME (month-end) or YE (year-end)"),
        rf: float = typer.Option(0.0, help="Risk-free rate (annual, decimal, e.g., 0.02)"),
        benchmark: Optional[str] = typer.Option(None, help="Benchmark ticker, e.g., ^GSPC"),
        plot_drawdown: bool = typer.Option(True, help="Plot drawdown chart"),
    ):
        controller_callback(
            "metrics",
            {
                "start": start,
                "end": end,
                "interval": interval,
                "freq": freq,
                "rf": rf,
                "benchmark": benchmark,
                "plot_drawdown": plot_drawdown,
            },
        )

    app()
