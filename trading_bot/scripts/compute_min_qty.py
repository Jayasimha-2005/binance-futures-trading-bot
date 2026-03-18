from bot.client import get_client
from decimal import Decimal, ROUND_UP


def ceil_step(q, step):
    qd = Decimal(q)
    sd = Decimal(step)
    n = (qd / sd).to_integral_value(rounding=ROUND_UP)
    return (n * sd).normalize()


def main():
    c = get_client()
    symbol = 'BTCUSDT'
    try:
        ticker = c.futures_symbol_ticker(symbol=symbol)
        price = Decimal(str(ticker.get('price') or ticker.get('lastPrice') or 0))
        info = c.futures_exchange_info()
        min_notional = None
        step_size = None
        for s in info.get('symbols', []):
            if s.get('symbol') == symbol:
                for f in s.get('filters', []):
                    t = f.get('filterType')
                    if t in ('NOTIONAL', 'MIN_NOTIONAL') and min_notional is None:
                        min_notional = Decimal(str(f.get('minNotional') or f.get('min_notional') or 0))
                    if t == 'LOT_SIZE' and step_size is None:
                        step_size = f.get('stepSize')
                break
        if min_notional is None:
            print('Could not determine min_notional from exchange info')
        else:
            qty_needed = (min_notional / price)
            if step_size:
                qty = ceil_step(qty_needed, step_size)
            else:
                qty = qty_needed.quantize(Decimal('0.00000001'), rounding=ROUND_UP)
            print('Symbol:', symbol)
            print('Price:', price)
            print('Min notional:', min_notional)
            print('Estimated minimum quantity:', qty)
            print('\nSuggested CLI:')
            print(f"python trading_bot/cli.py --symbol {symbol} --side BUY --type MARKET --quantity {qty}")
    except Exception as e:
        print('Error computing suggestion:', e)


if __name__ == '__main__':
    main()
