import pytest
from bot.validators import validate_order_params


def test_valid_market():
    side, typ = validate_order_params("buy", "market", 0.1)
    assert side == "BUY"
    assert typ == "MARKET"


def test_invalid_side():
    with pytest.raises(ValueError):
        validate_order_params("hold", "market", 0.1)


def test_limit_requires_price():
    with pytest.raises(ValueError):
        validate_order_params("buy", "limit", 0.1)


def test_stop_requires_price():
    with pytest.raises(ValueError):
        validate_order_params("sell", "stop", 0.1)
