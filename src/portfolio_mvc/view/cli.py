import typer

app = typer.Typer(help="Portfolio Management CLI")

def run_cli(controller_callback):
    """
    Sets up CLI commands and forwards user inputs to the Controller.
    """

    @app.command("add")
    def add(symbol: str, value: float):
        """
        Add a new asset to the portfolio.
        Example:
        python -m portfolio_mvc.controller.app add TSLA 1500
        """
        controller_callback("add", {"symbol": symbol, "value": value})

    @app.command("show")
    def show(plot: bool = False):
        """
        Display current portfolio table (and chart if --plot is used).
        Example:
        python -m portfolio_mvc.controller.app show --plot
        """
        controller_callback("show", {"plot": plot})

    @app.command("reset")
    def reset():
        """
        Clear all saved portfolio data.
        Example:
        python -m portfolio_mvc.controller.app reset
        """
        controller_callback("reset", {})

    @app.command("remove")
    def remove(symbol: str):
        """
        Remove an asset from the portfolio by its symbol.
        Example:
        python -m portfolio_mvc.controller.app remove TSLA
        """
        controller_callback("remove", {"symbol": symbol})

    app()

