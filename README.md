# 💼 Assignment Portfolio Tracker CLI (MVC Application)

A **command-line portfolio tracker** built in **Python**, using the **Model–View–Controller (MVC)** architecture.

It allows you to:
- Add, remove, view, and reset portfolio assets  
- Fetch and visualize **historical & current prices**  
- Calculate **total values and weights** per asset, sector, or asset class  
- Run **Monte Carlo portfolio simulations** over 15 years (100,000 paths by default)  
- Display **charts** (price series, pie weights, simulation histogram)

---

## ⚙️ Features

✅ **MVC Structure**
- **Model:** Handles data (assets, prices, simulations) and persistence via `assets.csv`
- **View:** Command-line interface (Typer) and charts (matplotlib)
- **Controller:** Manages data flow and user commands

✅ **Core Functionality**
- Add, remove, and reset assets  
- Show portfolio with current and purchase values  
- Group weights by **sector** or **asset class**  
- Retrieve and plot historical prices from Yahoo Finance  
- Run Monte Carlo simulations of portfolio growth  
- Visualize results via pie charts and histograms  

✅ **Extra Functions**
- You can see how the **total portfolio value** evolved historically.
- Compute **annualized return**, **volatility**, **Sharpe ratio**, and **max drawdown** for your current portfolio. Optionally compare against a **benchmark** (e.g., `^GSPC` for S&P 500) and visualize the **drawdown curve**.


---

## 🧩 Project Structure

```
portfolio-mvc/
├─ src/
│  └─ portfolio_mvc/
│     ├─ model/
│     │  ├─ assets.py
│     │  ├─ pricing.py
│     │  ├─ metrics.py
│     │  └─ simulate.py
│     ├─ view/
│     │  ├─ cli.py
│     │  ├─ tables.py
│     │  └─ charts.py
│     ├─ controller/
│     │  └─ app.py
│     └─ tests/
│        └─ test_assets.py
├─ requirements.txt
├─ README.md
├─ assets.csv
└─ .gitignore
```

---

## 🚀 Installation

```bash
# 1️⃣ Clone the repository
git clone https://github.com/thijsvandepasch/portfolio-mvc.git
cd portfolio-mvc

# 2️⃣ Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\Activate.ps1

# 3️⃣ Install dependencies
python3 -m pip install -r requirements.txt
```

If you see `ModuleNotFoundError: portfolio_mvc`, set your path:

```bash
export PYTHONPATH=src      # macOS/Linux
# $env:PYTHONPATH = "src"  # Windows PowerShell
```

---

## ▶️ Usage

All commands are run from the project root like this, so in the terminal of python:

```bash
python -m portfolio_mvc.controller.app <command> [options]
```

---

### 🟢 1) Add Assets

Add assets with ticker, sector, class, quantity, and purchase price:

```bash
python -m portfolio_mvc.controller.app add AAPL Technology Equity 10 180
python -m portfolio_mvc.controller.app add MSFT Technology Equity 5 320
```

---

### 🟡 2) View Portfolio

Show all holdings, transaction/current values, and weights:

```bash
python -m portfolio_mvc.controller.app show
```

Group by **sector** or **asset class** and show pie chart:

```bash
python -m portfolio_mvc.controller.app show --group sector
python -m portfolio_mvc.controller.app show --group asset_class --plot
```

---

### 🔵 3) View Prices & Charts

Plot historical prices for one or multiple tickers:

```bash
# Combined chart
python -m portfolio_mvc.controller.app prices AAPL MSFT --start 2020-01-01 --combine

# Separate charts
python -m portfolio_mvc.controller.app prices AAPL MSFT --start 2015-01-01 --no-combine
```

---

### 🔴 4) Simulate Portfolio

Run a 15-year simulation (default: 100k Monte Carlo paths):

```bash
python -m portfolio_mvc.controller.app simulate --freq ME
```

Optional flags:
```bash
--years <int>     # number of years (default 15)
--paths <int>     # number of simulation paths (default 100000)
--freq <YE|ME>    # annual or monthly return aggregation
--no-plot         # skip histogram plot
```

Example:
```bash
python -m portfolio_mvc.controller.app simulate --freq ME --paths 20000
```

> 💡 The histogram’s x-axis limit is set to `plt.xlim(0, 1_000_000)` for clarity.

---

### ⚫ 5) Remove or Reset Portfolio

Remove an individual ticker:

```bash
python -m portfolio_mvc.controller.app remove AAPL
```

Reset the entire portfolio:

```bash
python -m portfolio_mvc.controller.app reset
```

---


### 🟣 6) (Extra) Portfolio Performance Over Time

You can now analyze how your **total portfolio value** evolved historically using live market data.  

```bash
python -m portfolio_mvc.controller.app performance --start 2018-01-01 --freq ME
```

---



### 🟠 6) (Extra) Portfolio Return & Risk Metrics

Compute **annualized return**, **volatility**, **Sharpe ratio**, and **max drawdown** for your current portfolio. Optionally compare against a **benchmark** (e.g., `^GSPC` for S&P 500) and visualize the **drawdown curve**.


```bash
# Portfolio metrics with month-end aggregation and 2% risk-free rate
python -m portfolio_mvc.controller.app metrics --start 2018-01-01 --freq ME --rf 0.02

# Compare to S&P 500
python -m portfolio_mvc.controller.app metrics --start 2018-01-01 --freq ME --rf 0.02 --benchmark ^GSPC

# Skip drawdown plot
python -m portfolio_mvc.controller.app metrics --start 2018-01-01 --freq ME --no-plot-drawdown
```

---


## 🧪 Example Session

```bash
python -m portfolio_mvc.controller.app add AAPL Technology Equity 10 180
python -m portfolio_mvc.controller.app add MSFT Technology Equity 5 320
python -m portfolio_mvc.controller.app show
python -m portfolio_mvc.controller.app prices AAPL MSFT --start 2018-01-01 --combine
python -m portfolio_mvc.controller.app simulate --freq ME --paths 20000
python -m portfolio_mvc.controller.app reset
```

---

## 🧾 Dependencies

```
typer
rich
pandas
numpy
matplotlib
yfinance
pytest
```

Install manually if needed:

```bash
pip install typer rich pandas numpy matplotlib yfinance pytest
```

---

## 🧠 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: portfolio_mvc` | Run `export PYTHONPATH=src` |
| No chart appears | Ensure virtual environment active and matplotlib installed |
| “Insufficient history” during simulation | Use `--freq ME` and test with older tickers (e.g., AAPL, MSFT) |
| Yahoo API timeout | Wait a minute and retry (rate limiting) |

---

## 📜 License

MIT © 2025 Thijs van de Pasch
