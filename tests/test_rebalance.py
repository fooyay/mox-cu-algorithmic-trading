from typing import Any, cast

from script.rebalance import needs_rebalancing
from script.tokens import Portfolio, TokenPosition


class DummyToken:
    def __init__(self, raw_balance: int, decimals: int = 2):
        self._raw_balance = raw_balance
        self._decimals = decimals

    def balanceOf(self, _user: str) -> int:
        return self._raw_balance

    def decimals(self) -> int:
        return self._decimals


def _make_position(symbol: str, usd_value: float) -> TokenPosition:
    # With a price of 1.0 and 2 decimals, raw balance is usd_value * 100.
    a_token = cast(Any, DummyToken(raw_balance=int(usd_value * 100), decimals=2))
    token = cast(Any, object())
    return TokenPosition(
        symbol=symbol,
        underlying_symbol=symbol,
        token=token,
        a_token=a_token,
        recent_price=1.0,
    )


def test_needs_rebalancing_returns_false_when_within_buffer():
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            _make_position("USDC", 15.0),
            _make_position("WETH", 30.0),
            _make_position("WBTC", 50.0),
            _make_position("LINK", 5.0),
        ],
    )

    assert needs_rebalancing(portfolio) is False


def test_needs_rebalancing_returns_true_when_outside_buffer():
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            _make_position("USDC", 20.0),
            _make_position("WETH", 30.0),
            _make_position("WBTC", 45.0),
            _make_position("LINK", 5.0),
        ],
    )

    assert needs_rebalancing(portfolio) is True
