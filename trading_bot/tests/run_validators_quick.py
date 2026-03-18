from bot.validators import validate_order_params

# mirror tests in test_validators.py

try:
    side, typ = validate_order_params("buy", "market", 0.1)
    assert side == "BUY"
    assert typ == "MARKET"
    print('test_valid_market: OK')
except Exception as e:
    print('test_valid_market: FAIL', e)

try:
    try:
        validate_order_params("hold", "market", 0.1)
        print('test_invalid_side: FAIL (no exception)')
    except ValueError:
        print('test_invalid_side: OK')
except Exception as e:
    print('test_invalid_side: FAIL', e)

try:
    try:
        validate_order_params("buy", "limit", 0.1)
        print('test_limit_requires_price: FAIL (no exception)')
    except ValueError:
        print('test_limit_requires_price: OK')
except Exception as e:
    print('test_limit_requires_price: FAIL', e)

try:
    try:
        validate_order_params("sell", "stop", 0.1)
        print('test_stop_requires_price: FAIL (no exception)')
    except ValueError:
        print('test_stop_requires_price: OK')
except Exception as e:
    print('test_stop_requires_price: FAIL', e)
