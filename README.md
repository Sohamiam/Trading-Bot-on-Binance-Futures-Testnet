1 Create a virtual environment

python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

2. Install dependencies
pip install -r requirements.txt

3. Get Testnet credentials
Go to https://testnet.binancefuture.com
Log in (GitHub account works fine)
Generate API Key under Account settings
Copy the key and secret

4. Set up your .env file
Create a .env file in the project root:

BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

How to Run

Place a MARKET order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

Place a LIMIT order

python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 75000

Place a STOP_MARKET order

python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 60000

Pass credentials directly

python cli.py --symbol ETHUSDT --side BUY --type MARKET --quantity 0.1 \
  --api-key YOUR_KEY --api-secret YOUR_SECRET


  What the Output Looks Like-
───────────────────────────────────────────────────────
  ORDER SUMMARY (what we're about to send)
───────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
───────────────────────────────────────────────────────
  Confirm order? (yes/no): yes

  ORDER RESPONSE
───────────────────────────────────────────────────────
  Order ID     : 3256789
  Status       : FILLED
  Symbol       : BTCUSDT
  Side         : BUY
  Type         : MARKET
  Orig Qty     : 0.01
  Executed Qty : 0.01
  Avg Price    : 67234.50000
  Time in Force: GTC
  Update Time  : 1718458322543
───────────────────────────────────────────────────────

  ✓ Order placed successfully! Order ID: 3256789

Project Structure
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client (auth, signing, HTTP)
│   ├── orders.py          # Order placement logic
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Shared logger setup
├── logs/                  # Auto-created, timestamped log files
├── cli.py                 # CLI entry point (argparse)
├── .env                   # Your credentials (not committed)
├── README.md
└── requirements.txt

Assumptions
Tested against Binance Futures Testnet (USDT-M) only
Minimum quantity and price precision follows BTCUSDT testnet defaults —
if you hit a precision error, round your quantity to 3 decimal places
STOP_MARKET stop price should be set above current price for BUY,
below for SELL (standard Binance behavior)
Credentials are read from .env first, CLI flags second


Log Files
All runs write to /logs/trading_bot_YYYYMMDD_HHMMSS.log.
DEBUG level is written to file (full request/response detail).
INFO level is shown on console (clean, readable).

---

## Quick Validation Test (no API needed)

```bash
# Missing price on LIMIT — should give a clear error
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01

# OUTPUT:
#   INPUT ERROR: Price is required for LIMIT orders.

# Invalid side — caught immediately
python cli.py --symbol BTCUSDT --side HOLD --type MARKET --quantity 0.01

# OUTPUT:
# cli.py: error: argument --side: invalid choice: 'HOLD' (choose from 'BUY', 'SELL')

# Negative quantity
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity -5

# OUTPUT:
#   INPUT ERROR: Quantity must be greater than zero. Got: -5.0




  
