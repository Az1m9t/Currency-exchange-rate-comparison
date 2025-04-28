# Exchange Rate Bot — Async Telegram Bot for Comparing Currency Rates

This project is an **asynchronous Telegram bot** designed to fetch and compare live exchange rates of USD to RUB from various sources. It aggregates data in real time and displays a summary of current market spreads from reliable providers such as the Central Bank of Russia, Abcex.io, Investing.com, and ProFinance.

> **Why use this bot?**  
> Simple, extensible, real-time and fully asynchronous — perfect for financial analysts, traders, or anyone interested in exchange rate arbitrage.

---

## 🧠 Features

- 📉 **Live rate comparison** from:
  - **Rapira.net** (`USDTRUB` ask price)
  - **Central Bank of Russia (CBR)** (official XML daily rates)
  - **ProFinance** (custom parser)
  - **Investing.com** (WebSocket live ticker)
- ⚡ Built with **asyncio** + `aiohttp` + `websockets` for high performance.
- 🤖 Telegram bot interface powered by **aiogram**.
- 📲 Mobile-friendly UI using custom reply keyboards.
- 🔁 Periodic WebSocket reconnecting to Investing.com stream.
- 🧩 Easily extendable: plug in your own data sources by subclassing or injecting new fetchers.

---

## 📦 Structure

```bash
├── abcex.py              # Fetcher for abcex.io order book
├── cbr.py                # Fetcher for Central Bank of Russia (XML API)
├── invest_rep.py         # WebSocket handler for Investing.com real-time rates
├── profinance.py         # Parser for ProFinance USD/RUB
├── main.py               # Telegram bot logic (aiogram)
├── README.md             # You are here 🙂
```

---

## 🧪 Example Output

```text
📊 Rates Summary 📈

🔹 Rapira rate: 92.4567

🔸 CBR rate: 91.8976 | Spread: 0.6048%
🔸 ProFinance rate: 91.6000 | Spread: 0.9277%
🔸 Investing rate: 91.7800 | Spread: 0.7323%
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Az1m9t/Currency-exchange-rate-comparison.git
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

> Minimal dependencies:
> - `aiohttp`
> - `aiogram`
> - `websockets`

### 3. Set your Telegram Bot Token

Edit `main.py` and replace:
```python
TOKEN = "YOUR_BOT_TOKEN"
```

### 4. Run the bot

```bash
python main.py
```

---

## 🛠️ Extendability

Adding new sources is easy:

1. Create a new class with an `async def fetch_exchange_rate()` method.
2. Return a float-compatible exchange rate.
3. Plug it into `get_all_rates()` in `main_bot.py`.

That’s it. The spread will be automatically calculated and included.

---

## 📌 Use Cases

- Exchange rate monitoring
- Arbitrage calculations
- Educational purposes
- Financial dashboards
- Quick access to official + market rates

---

## 🧠 Technologies Used

- Python 3.10+
- `asyncio` for non-blocking concurrency
- `aiohttp` for async HTTP requests
- `websockets` for real-time streams
- `aiogram` for Telegram bot framework

---

## 🔐 Disclaimer

This bot is for **informational purposes only** and should not be used for trading decisions without verification from official sources.
