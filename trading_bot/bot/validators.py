"""Input validation helpers for order parameters."""

def validate_order_params(side, order_type, quantity, price=None, client=None, symbol=None):
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

    # Optional: validate minimum notional if client and symbol are provided
    if client is not None and symbol is not None:
        try:
            # Determine price to compute notional: use provided price for LIMIT/STOP, otherwise fetch market ticker
            if order_type == "MARKET":
                ticker = client.futures_symbol_ticker(symbol=symbol)
                price_for_notional = float(ticker.get("price") or ticker.get("lastPrice") or 0)
            else:
                price_for_notional = float(price)

            q = float(quantity)
            notional = q * price_for_notional

            info = client.futures_exchange_info()
            min_notional = None
            for s in info.get("symbols", []):
                if s.get("symbol") == symbol:
                    for f in s.get("filters", []):
                        # look for different filter types across client versions
                        if f.get("filterType") in ("NOTIONAL", "MIN_NOTIONAL"):
                            min_notional = float(f.get("minNotional") or f.get("minNotional", 0))
                            break
                    break

            if min_notional is not None and notional < min_notional:
                raise ValueError(f"Order's notional ({notional:.8f}) is below the minimum required {min_notional}")
        except Exception:
            # If validation cannot be performed (network/error), do not block order placement here
            pass

    return side, order_type
