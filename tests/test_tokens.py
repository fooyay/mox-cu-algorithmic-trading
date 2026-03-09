from script.tokens import (
    Portfolio,
    TokenPosition,
    _format_balance,
    _normalized_balance,
    _position_values_and_total,
    get_portfolio_value,
    get_portfolio_weights,
    show_aave_positions,
    show_balances,
    show_position_values,
)
from typing import Any, cast


class DummyToken:
    def __init__(self, symbol: str, raw_balance: int, decimals: int):
        self._symbol = symbol
        self._raw_balance = raw_balance
        self._decimals = decimals

    def symbol(self) -> str:
        return self._symbol

    def balanceOf(self, _user: str) -> int:
        return self._raw_balance

    def decimals(self) -> int:
        return self._decimals


def test_format_balance_scales_by_decimals():
    token = DummyToken("USDC", 150, 2)

    result = _format_balance(cast(Any, token), "0xabc")

    assert result == "1.5 (raw: 150)"


def test_normalized_balance_scales_by_decimals():
    token = DummyToken("USDC", 150, 2)

    result = _normalized_balance(cast(Any, token), "0xabc")

    assert result == 1.5


def test_format_balance_with_zero_decimals():
    token = DummyToken("WBTC", 42, 0)

    result = _format_balance(cast(Any, token), "0xabc")

    assert result == "42.0 (raw: 42)"


def test_show_balances_prints_header_and_each_token_balance(capsys):
    user = "0x123"
    tokens = [
        DummyToken("USDC", 2500, 2),
        DummyToken("WETH", 3 * 10**18, 18),
    ]

    show_balances(cast(Any, tokens), user)

    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()

    assert lines[0] == f"Balances for {user}:"
    assert lines[1] == "USDC: 25.0 (raw: 2500)"
    assert lines[2] == "WETH: 3.0 (raw: 3000000000000000000)"


def test_portfolio_holds_user_and_positions():
    user = "0xabc"
    usdc = cast(Any, DummyToken("USDC", 1_000_000, 6))
    positions = [
        TokenPosition(
            symbol="USDC",
            underlying_symbol="USDC",
            token=usdc,
            a_token=None,
        )
    ]

    portfolio = Portfolio(user=user, positions=positions)

    assert portfolio.user == user
    assert portfolio.positions == positions


def test_position_values_and_total_returns_usd_values_and_sum():
    user = "0xabc"
    token = cast(Any, object())
    # normalized balance = raw / 10**decimals; value = normalized * price
    usdc_a = cast(Any, DummyToken("USDC", raw_balance=100, decimals=2))  # 1.0 * 1.0 = 1.0
    weth_a = cast(Any, DummyToken("WETH", raw_balance=200, decimals=2))  # 2.0 * 3000.0 = 6000.0
    portfolio = Portfolio(
        user=user,
        positions=[
            TokenPosition(
                symbol="USDC",
                underlying_symbol="USDC",
                token=token,
                a_token=usdc_a,
                recent_price=1.0,
            ),
            TokenPosition(
                symbol="WETH",
                underlying_symbol="WETH",
                token=token,
                a_token=weth_a,
                recent_price=3000.0,
            ),
        ],
    )

    values, total = _position_values_and_total(portfolio)

    assert values == [1.0, 6000.0]
    assert total == 6001.0


def test_position_values_and_total_uses_zero_for_position_with_no_price():
    user = "0xabc"
    token = cast(Any, object())
    a_token = cast(Any, DummyToken("WETH", raw_balance=100, decimals=2))
    portfolio = Portfolio(
        user=user,
        positions=[
            TokenPosition(
                symbol="WETH",
                underlying_symbol="WETH",
                token=token,
                a_token=a_token,
                recent_price=None,
            )
        ],
    )

    values, total = _position_values_and_total(portfolio)

    assert values == [0.0]
    assert total == 0.0


def test_get_portfolio_value_sums_all_position_values():
    user = "0xabc"
    token = cast(Any, object())
    usdc_a = cast(Any, DummyToken("USDC", raw_balance=500, decimals=2))  # 5.0 * 1.0 = 5.0
    weth_a = cast(Any, DummyToken("WETH", raw_balance=200, decimals=2))  # 2.0 * 1.0 = 2.0
    portfolio = Portfolio(
        user=user,
        positions=[
            TokenPosition(
                symbol="USDC",
                underlying_symbol="USDC",
                token=token,
                a_token=usdc_a,
                recent_price=1.0,
            ),
            TokenPosition(
                symbol="WETH",
                underlying_symbol="WETH",
                token=token,
                a_token=weth_a,
                recent_price=1.0,
            ),
        ],
    )

    assert get_portfolio_value(portfolio) == 7.0


def test_get_portfolio_value_returns_zero_for_empty_portfolio():
    portfolio = Portfolio(user="0xabc", positions=[])

    assert get_portfolio_value(portfolio) == 0.0


def test_show_aave_positions_prints_header_and_each_position(capsys):
    user = "0xabc"
    token = cast(Any, object())
    usdc_a = cast(Any, DummyToken("USDC", raw_balance=100, decimals=2))
    weth_a = cast(Any, DummyToken("WETH", raw_balance=200, decimals=2))
    portfolio = Portfolio(
        user=user,
        positions=[
            TokenPosition(
                symbol="USDC",
                underlying_symbol="USDC",
                token=token,
                a_token=usdc_a,
            ),
            TokenPosition(
                symbol="WETH",
                underlying_symbol="WETH",
                token=token,
                a_token=weth_a,
            ),
        ],
    )

    show_aave_positions(portfolio)

    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "Aave positions:"
    assert lines[1].startswith("USDC:")
    assert lines[2].startswith("WETH:")


def test_show_position_values_prints_usd_value_per_position(capsys):
    user = "0xabc"
    token = cast(Any, object())
    usdc_a = cast(Any, DummyToken("USDC", raw_balance=100, decimals=2))  # 1.0 * $1.0  = $1.00
    weth_a = cast(Any, DummyToken("WETH", raw_balance=100, decimals=2))  # 1.0 * $3000 = $3000.00
    portfolio = Portfolio(
        user=user,
        positions=[
            TokenPosition(
                symbol="USDC",
                underlying_symbol="USDC",
                token=token,
                a_token=usdc_a,
                recent_price=1.0,
            ),
            TokenPosition(
                symbol="WETH",
                underlying_symbol="WETH",
                token=token,
                a_token=weth_a,
                recent_price=3000.0,
            ),
        ],
    )

    show_position_values(portfolio)

    captured = capsys.readouterr()
    assert "USDC: 1.00 USD" in captured.out
    assert "WETH: 3000.00 USD" in captured.out


def test_get_portfolio_weights_returns_expected_normalized_weights():
    user = "0xabc"
    usdc = cast(Any, DummyToken("USDC", 1_500, 2))
    weth = cast(Any, DummyToken("WETH", 3_000, 2))
    token = cast(Any, object())
    portfolio = Portfolio(
        user=user,
        positions=[
            TokenPosition(
                symbol="USDC",
                underlying_symbol="USDC",
                token=token,
                a_token=usdc,
                recent_price=1.0,
            ),
            TokenPosition(
                symbol="WETH",
                underlying_symbol="WETH",
                token=token,
                a_token=weth,
                recent_price=1.0,
            ),
        ],
    )

    weights = get_portfolio_weights(portfolio)

    assert weights == {"USDC": 1 / 3, "WETH": 2 / 3}
