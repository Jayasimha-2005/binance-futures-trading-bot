"""Input validation helpers for order parameters."""

def validate_order_params(side, order_type, quantity, price=None):
    if isinstance(side, str):
        side = side.upper()
    if isinstance(order_type, str):
        order_type = order_type.upper()

    if side not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")

    if order_type not in ("MARKET", "LIMIT", "STOP"):
        raise ValueError("order_type must be MARKET, LIMIT, or STOP")

    try:
        q = float(quantity)
    except Exception:
        raise ValueError("quantity must be a number")

    if q <= 0:
        raise ValueError("quantity must be > 0")

    if order_type in ("LIMIT", "STOP"):
        if price is None:
            raise ValueError("price is required for LIMIT and STOP orders")
        try:
            p = float(price)
        except Exception:
            raise ValueError("price must be a number")
        if p <= 0:
            raise ValueError("price must be > 0")

    return side, order_type
