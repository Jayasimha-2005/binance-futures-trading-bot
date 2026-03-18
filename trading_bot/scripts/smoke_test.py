"""Smoke test script: places one MARKET and one LIMIT order using .env keys.

This is intended to run locally with testnet keys in `.env`.
"""
from bot.client import get_client
from bot.orders import place_order
import logging


def run():
    client = get_client()

    try:
        print("Running MARKET order test...")
        m = place_order(client, "BTCUSDT", "BUY", "MARKET", 0.002)
        print("MARKET result:", m)
    except Exception as e:
        logging.exception("Market order failed: %s", e)

    try:
        print("Running LIMIT order test...")
        l = place_order(client, "BTCUSDT", "SELL", "LIMIT", 0.002, price=70000)
        print("LIMIT result:", l)
    except Exception as e:
        logging.exception("Limit order failed: %s", e)


if __name__ == "__main__":
    run()
