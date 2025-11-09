from rich.table import Table
from rich.console import Console
import pandas as pd

def print_assets(df: pd.DataFrame) -> None:
    """
    Pretty table for assets/weights in the terminal.
    """
    console = Console()
    if df.empty:
        console.print("[bold yellow]No assets yet.[/bold yellow]")
        return

    tbl = Table(title="Assets")
    for col in df.columns:
        tbl.add_column(col, justify="right" if col != "symbol" else "left")
    for _, row in df.iterrows():
        cells = []
        for v in row.values:
            cells.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        tbl.add_row(*cells)
    console.print(tbl)