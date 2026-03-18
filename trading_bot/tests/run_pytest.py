import sys
import os
# Ensure the package root (`trading_bot`) is on sys.path so tests can import `bot`.
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
import pytest

if __name__ == '__main__':
    pytest.main(['-q', 'trading_bot/tests'])
