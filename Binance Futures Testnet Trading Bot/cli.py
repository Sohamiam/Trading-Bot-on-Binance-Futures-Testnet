#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot — CLI Entry Point
Author: Built for application task

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 50000
  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 40000
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.logging_config import setup_logger
from bot.orders import place_order
from bot.validators import validate_all

load_dotenv()
logger = setup_logger("trading_bot.cli")


def print_separator():
    print("\n" + "─" * 55)


def print_order_summary(params: dict):
    print_separator()
    print("  ORDER SUMMARY (what we're about to send)")
    print_separator()
    print(f"  Symbol     : {params['symbol']}")
    print(f"  Side       : {params['side']}")
    print(f"  Type       : {params['order_type']}")
    print(f"  Quantity   : {params['quantity']}")
    if params.get("price"):
        print(f"  Price      : {params['price']}")
    if params.get("stop_price"):
        print(f"  Stop Price : {params['stop_price']}")
    print_separator()


def print_order_response(response: dict):
    print("\n  ORDER RESPONSE")
    print_separator()
    print(f"  Order ID     : {response.get('orderId', 'N/A')}")
    print(f"  Status       : {response.get('status', 'N/A')}")
    print(f"  Symbol       : {response.get('symbol', 'N/A')}")
    print(f"  Side         : {response.get('side', 'N/A')}")
    print(f"  Type         : {response.get('type', 'N/A')}")
    print(f"  Orig Qty     : {response.get('origQty', 'N/A')}")
    print(f"  Executed Qty : {response.get('executedQty', 'N/A')}")

    avg_price = response.get("avgPrice", "0")
    if avg_price and float(avg_price) > 0:
        print(f"  Avg Price    : {avg_price}")
    else:
        print(f"  Avg Price    : N/A (not yet filled)")

    print(f"  Time in Force: {response.get('timeInForce', 'N/A')}")
    print(f"  Update Time  : {response.get('updateTime', 'N/A')}")
    print_separator()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet — Place MARKET, LIMIT, or STOP_MARKET orders.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 2000
  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 40000
        """
    )

    parser.add_argument(
        "--symbol", required=True,
        help="Trading pair, e.g. BTCUSDT"
    )
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL"],
        help="Order side: BUY or SELL"
    )
    parser.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type: MARKET, LIMIT, or STOP_MARKET"
    )
    parser.add_argument(
        "--quantity", required=True,
        help="Quantity to trade (e.g. 0.01 for BTC)"
    )
    parser.add_argument(
        "--price", default=None,
        help="Limit price — required for LIMIT orders"
    )
    parser.add_argument(
        "--stop-price", dest="stop_price", default=None,
        help="Stop price — required for STOP_MARKET orders"
    )
    parser.add_argument(
        "--api-key", default=None,
        help="Binance API key (or set BINANCE_API_KEY in .env)"
    )
    parser.add_argument(
        "--api-secret", default=None,
        help="Binance API secret (or set BINANCE_API_SECRET in .env)"
    )

    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    # ── Resolve credentials ──────────────────────────────────────────────────
    api_key = args.api_key or os.getenv("BINANCE_API_KEY")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("API credentials not found. Set BINANCE_API_KEY and BINANCE_API_SECRET in .env or pass via flags.")
        print("\n  ERROR: Missing API credentials.")
        print("  Set them in a .env file or pass --api-key / --api-secret flags.\n")
        sys.exit(1)

    # ── Validate inputs ──────────────────────────────────────────────────────
    logger.info(f"Raw CLI input — symbol={args.symbol} side={args.side} type={args.order_type} qty={args.quantity}")

    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as e:
        logger.error(f"Validation failed: {e}")
        print(f"\n  INPUT ERROR: {e}\n")
        sys.exit(1)

    # ── Show what we're about to do ──────────────────────────────────────────
    print_order_summary(validated)

    # ── Confirm before firing ────────────────────────────────────────────────
    confirm = input("  Confirm order? (yes/no): ").strip().lower()
    if confirm not in ("yes", "y"):
        logger.info("Order cancelled by user at confirmation prompt.")
        print("\n  Order cancelled.\n")
        sys.exit(0)

    # ── Build client and place order ─────────────────────────────────────────
    try:
        client = BinanceClient(api_key=api_key, api_secret=api_secret)

        response = place_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated.get("price"),
            stop_price=validated.get("stop_price"),
        )

        print_order_response(response)
        print(f"\n  ✓ Order placed successfully! Order ID: {response.get('orderId')}\n")
        logger.info("CLI completed successfully.")

    except ValueError as e:
        # Binance API-level errors (bad symbol, insufficient balance, etc.)
        logger.error(f"Order failed — API error: {e}")
        print(f"\n  API ERROR: {e}\n")
        sys.exit(1)

    except ConnectionError as e:
        logger.error(f"Order failed — network error: {e}")
        print(f"\n  NETWORK ERROR: {e}\n")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n  UNEXPECTED ERROR: {e}")
        print("  Check the log file in /logs for full details.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()