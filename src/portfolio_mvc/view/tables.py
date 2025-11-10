from rich.table import Table
from rich.console import Console
import pandas as pd

def _fmt(v):
    return f"{v:.4f}" if isinstance(v, float) else ("" if v is None else str(v))

def print_assets_full(df: pd.DataFrame) -> None:
    console = Console()
    if df.empty:
        console.print("[bold yellow]No assets yet.[/bold yellow]")
        return

    cols = ["symbol","sector","asset_class","quantity","purchase_price","transaction_value","current_price","current_value","weight"]
    show_cols = [c for c in cols if c in df.columns]
    tbl = Table(title="Portfolio")
    for col in show_cols:
        tbl.add_column(col, justify="right" if col not in ("symbol","sector","asset_class") else "left")
    for _, row in df[show_cols].iterrows():
       tbl.add_row(*[_fmt(v) for v in row.values])
    console.print(tbl)

def print_grouped(df_grp: pd.DataFrame, title: str) -> None:
    console = Console()
    if df_grp.empty:
        console.print(f"[bold yellow]No data for {title}[/bold yellow]")
        return
    
    tbl = Table(title=title)
    for col in df_grp.columns:
        tbl.add_column(col, justify="right" if col != df_grp.columns[0] else "left")
    for _, row in df_grp.iterrows():
        tbl.add_row(*[_fmt(v) for v in row.values])
    console.print(tbl)

def print_total(total: float) -> None:
    Console().print(f"[bold]Total current value:[/bold] {total:,.2f}")
    