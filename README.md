# Binance Futures Testnet Trading Bot

Small Python app to place MARKET, LIMIT, and STOP (Stop-Limit) orders on Binance Futures Testnet (USDT-M).

Prerequisites
- Python 3.8+
- Create Binance Futures Testnet API keys at https://testnet.binancefuture.com (API Management)

Getting started (from scratch)

1. Clone the repo or unzip the submission and open a terminal in the `trading_bot` folder.

2. Create and activate a virtual environment (recommended).

Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Create your `.env` from the example and populate keys (DO NOT commit this file):

Windows:
```powershell
copy .env.example .env
# edit .env and set API_KEY and API_SECRET
```

Linux / macOS:
```bash
cp .env.example .env
# edit .env and set API_KEY and API_SECRET
```

Set `BASE_URL=https://testnet.binancefuture.com` in `.env`. If you see timestamp/recvWindow errors, try `https://testnet.binancefuture.com/fapi` instead.

Setup
1. From `trading_bot` folder install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set your testnet keys and base URL:

Windows:
```powershell
copy .env.example .env
# Edit .env and set API_KEY, API_SECRET, BASE_URL=https://testnet.binancefuture.com
```

Usage

Place a MARKET order:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Place a LIMIT order:

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 60000
```

What the app does
- Validates inputs (`bot/validators.py`)
- Initializes a Binance client using keys from `.env` (`bot/client.py`)
- Places MARKET or LIMIT orders (`bot/orders.py`)
- Logs requests, responses, and errors to `logs/bot.log` (`bot/logging_config.py`)

Testing

Unit tests (validators):

```bash
# from repository root
python -m pytest trading_bot/tests
```

Smoke test (places one MARKET and one LIMIT order using `.env` keys):

```bash
python trading_bot/scripts/smoke_test.py
```

CLI examples

```bash
# MARKET
python trading_bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002

# LIMIT
python trading_bot/cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 70000

# STOP (Stop-Limit) — note: stop orders may be pending
python trading_bot/cli.py --symbol BTCUSDT --side BUY --type STOP --quantity 0.002 --price 82000
```

Log file
- `logs/bot.log` will contain timestamped entries for order requests and responses.

STOP orders note
- Some STOP/ALGO orders on Binance Futures Testnet may return limited fields immediately (no `orderId`).
- This project attempts to fetch full details after submission by polling `futures_get_order` and scanning open orders; in some cases the exchange returns details later or via different endpoints.

Sample structured log (JSON line):
```
{"timestamp":"2026-03-18T13:29:26Z","level":"INFO","event":"order_request","params":{"symbol":"BTCUSDT","side":"BUY","type":"STOP","quantity":0.002,"price":"76000"}}
{"timestamp":"2026-03-18T13:29:26Z","level":"INFO","event":"order_response","response":{"orderId":12861743459,"status":"NEW","executedQty":"0.000","avgPrice":"0.00"}}
```

## Notes on STOP Orders

Binance Futures STOP (algo) orders may not immediately return a standard `orderId` in their API response. To handle this asynchronous behavior the application:

- Generates a unique `clientOrderId` for each request (prefixed with `bot-...`).
- Uses the `clientOrderId` to track and correlate orders in logs and API calls.
- Attempts to fetch order details via polling (`futures_get_order`) and by scanning open/recent orders when the exchange does not return a conventional `orderId` immediately.

This approach ensures reliable order tracking even when the exchange response is asynchronous or delayed.

Notes & Assumptions
- This project uses the `python-binance` library; different versions expose different client attributes. Set `BASE_URL` in `.env` to `https://testnet.binancefuture.com` or `https://testnet.binancefuture.com/fapi` if you encounter timestamp errors./
- Do NOT commit real API keys to version control.
- For submissions, run one MARKET and one LIMIT order and include `logs/bot.log` showing the requests and responses.

Git hygiene (important)

- Add `.env` to `.gitignore` (already included) and never commit API keys.
- If you accidentally committed secrets, remove them from history before sharing (example using git filter-branch or BFG). Example quick commands:

```bash
# remove file from history (example, be careful — rewrites history)
git rm --cached trading_bot/.env
git commit -m "Remove .env"
# Use BFG or git filter-branch to fully purge secrets from history if needed
```

Logs & submission

- Keep the `trading_bot/logs/bot.log` file showing one MARKET, one LIMIT, and one STOP (clientOrderId) entry.
- Share the repo (after removing secrets) or a zip containing source code and the log file for evaluation.

Troubleshooting
- Invalid API Key: verify `.env` values
- Timestamp/recvWindow error: try using the `/fapi` base URL in `BASE_URL`
- Insufficient balance: add funds in Testnet Futures Wallet (faucet)

Next steps (optional enhancements)
- Structured JSON logging
- Add Stop-Limit / OCO order type
- Improve CLI UX with Typer or Click
