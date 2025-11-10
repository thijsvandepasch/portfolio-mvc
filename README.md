# 💼 Portfolio Management CLI (MVC Application)

This is a **command-line interface (CLI)** portfolio manager built in **Python**, following the **Model–View–Controller (MVC)** architecture.  
It allows you to add, remove, view, and reset financial assets, and visualize portfolio weights using a pie chart.

---

## ⚙️ Features

✅ Model–View–Controller architecture:
- **Model:** Handles asset data, calculations, and CSV storage (`assets.csv`)
- **View:** Command-line interface built with [Typer](https://typer.tiangolo.com/) and optional matplotlib charts
- **Controller:** Connects commands between Model and View

✅ Core functionality:
- Add new assets with ticker symbol and value  
- Remove individual assets  
- View portfolio table and visualize weights (`--plot`)  
- Reset the entire portfolio (deletes saved data)  
- Persistent storage between runs via CSV  
- Unit tests included (pytest)

---

## 🧩 Installation

### 1️⃣ Clone or download the repository

```bash
git clone https://github.com/thijsvandepasch/portfolio-mvc.git
cd portfolio-mvc