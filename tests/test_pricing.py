from typing import Any, cast

from script.pricing import get_price, update_portfolio_prices, update_prices
from script.tokens import Portfolio, TokenPosition


class DummyFeed:
    def __init__(self, raw_price: int, decimals: int):
        self._raw_price = raw_price
        self._decimals = decimals

    def latestRoundData(self):
        return (0, self._raw_price, 0, 0, 0)

    def decimals(self) -> int:
        return self._decimals


class DummyNetwork:
    def __init__(self, feeds_by_name: dict[str, DummyFeed]):
        self._feeds_by_name = feeds_by_name

    def manifest_named(self, name: str) -> DummyFeed:
        return self._feeds_by_name[name]


def _make_position(symbol: str, underlying_symbol: str) -> TokenPosition:
    token = cast(Any, object())
    return TokenPosition(
        symbol=symbol,
        underlying_symbol=underlying_symbol,
        token=token,
        a_token=None,
        recent_price=None,
    )


def test_get_price_scales_using_feed_decimals():
    network = DummyNetwork({"eth_usd_price_feed": DummyFeed(raw_price=2500_00000000, decimals=8)})

    result = get_price(symbol="ETH", network=cast(Any, network))

    assert result == 2500.0


def test_update_prices_returns_new_positions_with_recent_price():
    network = DummyNetwork(
        {
            "eth_usd_price_feed": DummyFeed(raw_price=3000_00000000, decimals=8),
            "usdc_usd_price_feed": DummyFeed(raw_price=1_00000000, decimals=8),
        }
    )
    positions = [
        _make_position(symbol="WETH", underlying_symbol="ETH"),
        _make_position(symbol="USDC", underlying_symbol="USDC"),
    ]

    updated = update_prices(token_positions=positions, network=cast(Any, network))

    assert updated is not positions
    assert [position.recent_price for position in updated] == [3000.0, 1.0]
    assert [position.recent_price for position in positions] == [None, None]


def test_update_portfolio_prices_returns_new_portfolio_with_updated_positions():
    network = DummyNetwork(
        {
            "eth_usd_price_feed": DummyFeed(raw_price=3200_00000000, decimals=8),
            "usdc_usd_price_feed": DummyFeed(raw_price=1_00000000, decimals=8),
        }
    )
    positions = [
        _make_position(symbol="WETH", underlying_symbol="ETH"),
        _make_position(symbol="USDC", underlying_symbol="USDC"),
    ]
    portfolio = Portfolio(user="0xabc", positions=positions)

    updated_portfolio = update_portfolio_prices(
        portfolio=portfolio,
        network=cast(Any, network),
    )

    assert updated_portfolio is not portfolio
    assert updated_portfolio.user == portfolio.user
    assert [position.recent_price for position in updated_portfolio.positions] == [3200.0, 1.0]
    assert [position.recent_price for position in portfolio.positions] == [None, None]
