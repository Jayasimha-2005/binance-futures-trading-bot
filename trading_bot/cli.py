"""CLI entrypoint for placing orders via Binance Futures Testnet."""
import argparse
import logging
import sys
from binance.exceptions import BinanceAPIException

from bot.client import get_client
from bot.orders import place_order, normalize_response
from bot.validators import validate_order_params


def parse_args():
    p = argparse.ArgumentParser(description="Place orders on Binance Futures Testnet")
    p.add_argument("--symbol", required=True, help="Trading pair symbol (e.g. BTCUSDT)")
    p.add_argument("--side", required=True, help="BUY or SELL")
    p.add_argument("--type", dest="order_type", required=True, help="MARKET, LIMIT, or STOP")
    p.add_argument("--quantity", required=True, help="Quantity to trade")
    p.add_argument("--price", required=False, help="Price for LIMIT or STOP orders")
    return p.parse_args()


def main():
    args = parse_args()

    try:
        client = get_client()
    except Exception as e:
        print(f"Failed to create Binance client: {e}")
        sys.exit(1)

    try:
        # basic validation; pass client+symbol to enable min-notional checks
        validate_order_params(args.side, args.order_type, args.quantity, args.price, client=client, symbol=args.symbol)
    except ValueError as e:
        print(f"Invalid input: {e}")
        sys.exit(1)

    try:
        resp = place_order(
            client,
            args.symbol,
            args.side,
            args.order_type,
            args.quantity,
            price=args.price,
        )

        norm = normalize_response(resp)

        print("===== ORDER RESULT =====")
        order_id = norm.get("orderId") or norm.get("clientOrderId")
        status = norm.get("status")
        executed = norm.get("executedQty")
        avg_price = norm.get("avgPrice")

        print(f"orderId: {order_id}")
        print(f"status: {status}")
        print(f"executedQty: {executed}")
        print(f"avgPrice: {avg_price}")

        if status is None:
            # Provide clearer feedback for pending STOP orders
            if args.order_type and args.order_type.upper() == "STOP":
                print("Note: STOP order placed (pending trigger on exchange). Use the shown clientOrderId to track this order.")
            else:
                print("Note: Order status not available yet; it may be pending on the exchange.")
        else:
            print("Order placed successfully")

    except BinanceAPIException as api_err:
        logging.exception("Binance API error placing order")
        print(f"Binance API error: {api_err}")
        sys.exit(1)
    except Exception as e:
        logging.exception("Order failed")
        print(f"Order failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
