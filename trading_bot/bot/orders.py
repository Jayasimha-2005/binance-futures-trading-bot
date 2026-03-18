"""Order execution helpers for Binance Futures (testnet).

Adds normalization for responses and support for STOP orders.
Includes polling to fetch detailed status for STOP orders when exchange returns limited info.
"""
import logging
import time
import uuid
from typing import Optional, Dict, Any
from .validators import validate_order_params


def normalize_response(response) -> dict:
    """Normalize API response to a consistent dict.

    Extracts: orderId, status, executedQty, avgPrice.
    """
    if not isinstance(response, dict):
        return {"orderId": None, "status": None, "executedQty": None, "avgPrice": "N/A"}

    order_id = response.get("orderId") or response.get("order_id") or response.get("clientOrderId")
    status = response.get("status")
    executed = response.get("executedQty") or response.get("cumQty") or response.get("executed_qty")
    avg = response.get("avgPrice") or response.get("avg_price") or "N/A"

    # Normalize numeric strings
    try:
        if executed is not None:
            executed = str(executed)
    except Exception:
        executed = str(executed)

    client_coid = response.get("clientOrderId") or response.get("origClientOrderId")
    return {"orderId": order_id, "status": status, "executedQty": executed, "avgPrice": avg, "clientOrderId": client_coid}


def place_order(client, symbol, side, order_type, quantity, price=None):
    """Place MARKET, LIMIT or STOP orders via the provided Binance client.

    Returns the raw API response (and logs the normalized response).
    """
    side, order_type = validate_order_params(side, order_type, quantity, price)

    def fetch_order_status(order_id: int) -> Optional[Dict[str, Any]]:
        """Attempt to fetch a single order by `orderId` with retries."""
        attempts = 15
        for _ in range(attempts):
            try:
                detailed = client.futures_get_order(symbol=symbol, orderId=order_id)
                return detailed
            except Exception:
                time.sleep(1)
        return None

    def find_recent_matching_open_order(client_coid: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fallback: scan open orders for a matching order (by symbol/price/side/quantity/clientOrderId)."""
        try:
            open_orders = client.futures_get_open_orders(symbol=symbol)
            for o in open_orders:
                try:
                    # Prefer matching by provided clientOrderId if available
                    coid = o.get("clientOrderId") or o.get("origClientOrderId")
                    if client_coid and coid and client_coid == coid:
                        return o

                    # Otherwise, try to match by response's clientOrderId if present
                    if not client_coid and isinstance(resp, dict):
                        resp_coid = resp.get("clientOrderId") or resp.get("origClientOrderId")
                        if resp_coid and coid and resp_coid == coid:
                            return o
                    if (
                        str(o.get("price")) == str(price)
                        and o.get("side") == side
                        and float(o.get("origQty", 0)) == float(quantity)
                    ):
                        return o
                except Exception:
                    continue
        except Exception:
            return None
        return None

    def find_recent_matching_order_all(client_coid: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Scan recent orders (all orders) for a matching clientOrderId or attributes."""
        try:
            all_orders = client.futures_get_all_orders(symbol=symbol, limit=100)
            for o in all_orders:
                try:
                    coid = o.get("clientOrderId") or o.get("origClientOrderId")
                    if client_coid and coid and client_coid == coid:
                        return o
                    if (
                        str(o.get("price")) == str(price)
                        and o.get("side") == side
                        and float(o.get("origQty", 0)) == float(quantity)
                    ):
                        return o
                except Exception:
                    continue
        except Exception:
            return None
        return None

    try:
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": float(quantity),
        }

        # Generate a clientOrderId we can use to reliably find the order later
        client_coid = f"bot-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        # include both commonly accepted keys
        params.update({"newClientOrderId": client_coid, "clientOrderId": client_coid})

        if order_type == "LIMIT":
            params.update({"price": str(price), "timeInForce": "GTC"})
        elif order_type == "STOP":
            # Stop-Limit order: set price and stopPrice (trigger)
            params.update({"price": str(price), "stopPrice": str(price), "timeInForce": "GTC"})

        logging.info("order_request", extra={"event": "order_request", "params": params, "clientOrderId": client_coid})

        # Prefer futures-specific endpoint if available
        if hasattr(client, "futures_create_order"):
            resp = client.futures_create_order(**params)
        else:
            resp = client.create_order(**params)

        # If this is a STOP order, try to fetch more detailed status when possible
        try:
            resp_order_id = None
            if isinstance(resp, dict):
                resp_order_id = resp.get("orderId") or resp.get("order_id")

            detailed = None
            if order_type == "STOP":
                if resp_order_id:
                    detailed = fetch_order_status(resp_order_id)
                else:
                    # try to discover the matching order using our generated clientOrderId
                    detailed = find_recent_matching_open_order(client_coid)
                    if not detailed:
                        detailed = find_recent_matching_order_all(client_coid)

                if detailed:
                    resp = detailed

        except Exception:
            logging.debug("Could not fetch detailed STOP order status")

        # Ensure clientOrderId is present in the returned dict so callers can display it
        try:
            if isinstance(resp, dict) and client_coid and not resp.get("clientOrderId"):
                resp["clientOrderId"] = client_coid
        except Exception:
            pass

        norm = normalize_response(resp)
        # If orderId is missing, include clientOrderId in normalized output
        if not norm.get("orderId"):
            norm["clientOrderId"] = client_coid

        logging.info("order_response", extra={"event": "order_response", "response": norm, "clientOrderId": client_coid})
        return resp

    except Exception:
        logging.exception("Error placing order", exc_info=True, extra={"event": "error", "params": params})
        raise
