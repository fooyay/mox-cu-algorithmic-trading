from typing import Any, cast

import script.rebalance as rebalance_module
from script.rebalance import _compute_pending_trades, needs_rebalancing, rebalance
from script.tokens import Portfolio, TokenPosition


class DummyToken:
    def __init__(self, raw_balance: int, decimals: int = 2):
        self._raw_balance = raw_balance
        self._decimals = decimals

    def balanceOf(self, _user: str) -> int:
        return self._raw_balance

    def decimals(self) -> int:
        return self._decimals


def _make_position(symbol: str, usd_value: float, target_weight: float | None = None) -> TokenPosition:
    # With a price of 1.0 and 2 decimals, raw balance is usd_value * 100.
    a_token = cast(Any, DummyToken(raw_balance=int(usd_value * 100), decimals=2))
    token = cast(Any, object())
    return TokenPosition(
        symbol=symbol,
        underlying_symbol=symbol,
        token=token,
        a_token=a_token,
        recent_price=1.0,
        target_weight=target_weight,
    )


def test_needs_rebalancing_returns_false_when_within_buffer():
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            _make_position("USDC", 15.0, target_weight=0.15),
            _make_position("WETH", 30.0, target_weight=0.30),
            _make_position("WBTC", 50.0, target_weight=0.50),
            _make_position("LINK", 5.0, target_weight=0.05),
        ],
    )

    assert needs_rebalancing(portfolio) is False


def test_needs_rebalancing_returns_true_when_outside_buffer():
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            _make_position("USDC", 20.0, target_weight=0.15),
            _make_position("WETH", 30.0, target_weight=0.30),
            _make_position("WBTC", 45.0, target_weight=0.50),
            _make_position("LINK", 5.0, target_weight=0.05),
        ],
    )

    assert needs_rebalancing(portfolio) is True


# --- needs_rebalancing edge cases ---


def test_needs_rebalancing_returns_false_for_empty_portfolio():
    portfolio = Portfolio(user="0xabc", positions=[])

    assert needs_rebalancing(portfolio) is False


def test_needs_rebalancing_returns_true_when_token_has_balance_but_no_target_weight():
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            _make_position("USDC", 50.0, target_weight=0.50),
            _make_position("WETH", 50.0, target_weight=None),  # no target → should rebalance
        ],
    )

    assert needs_rebalancing(portfolio) is True


def test_needs_rebalancing_returns_false_when_all_diffs_are_below_buffer():
    # WETH diff ≈ 0.005 (30.5/100 − 0.30), well below BUFFER (0.01)
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            _make_position("WETH", 30.5, target_weight=0.30),
            _make_position("USDC", 69.5, target_weight=0.70),
        ],
    )

    assert needs_rebalancing(portfolio) is False


# --- _compute_pending_trades ---


def test_compute_pending_trades_marks_overweight_tokens_as_positive_delta():
    # WETH current 40%, target 30% → overweight by 10% of $100 = +$10
    positions = [
        _make_position("USDC", 60.0, target_weight=0.60),
        _make_position("WETH", 40.0, target_weight=0.30),
    ]
    current_weights = {"USDC": 0.60, "WETH": 0.40}

    result = _compute_pending_trades(
        positions=positions, current_weights=current_weights, portfolio_value=100.0
    )

    assert "WETH" in result
    assert result["WETH"] > 0
    assert abs(result["WETH"] - 10.0) < 1e-9


def test_compute_pending_trades_marks_underweight_tokens_as_negative_delta():
    # WETH current 20%, target 30% → underweight by 10% of $100 = -$10
    positions = [
        _make_position("USDC", 80.0, target_weight=0.80),
        _make_position("WETH", 20.0, target_weight=0.30),
    ]
    current_weights = {"USDC": 0.80, "WETH": 0.20}

    result = _compute_pending_trades(
        positions=positions, current_weights=current_weights, portfolio_value=100.0
    )

    assert "WETH" in result
    assert result["WETH"] < 0
    assert abs(result["WETH"] - (-10.0)) < 1e-9


def test_compute_pending_trades_omits_tokens_within_buffer():
    # WETH diff = 0.305 - 0.30 = 0.005 < BUFFER (0.01) → omitted
    positions = [
        _make_position("USDC", 69.5, target_weight=0.695),
        _make_position("WETH", 30.5, target_weight=0.30),
    ]
    current_weights = {"USDC": 0.695, "WETH": 0.305}

    result = _compute_pending_trades(
        positions=positions, current_weights=current_weights, portfolio_value=100.0
    )

    assert "WETH" not in result


# --- rebalance orchestration ---


def test_rebalance_calls_withdraw_usdc_and_deposit_usdc(monkeypatch):
    calls: list[str] = []
    monkeypatch.setattr(rebalance_module, "withdraw_usdc", lambda p: calls.append("withdraw_usdc"))
    monkeypatch.setattr(rebalance_module, "deposit_usdc", lambda p: calls.append("deposit_usdc"))
    monkeypatch.setattr(rebalance_module, "sell_all", lambda *a, **kw: None)
    monkeypatch.setattr(rebalance_module, "sell_token_for_usdc", lambda **kw: None)
    monkeypatch.setattr(rebalance_module, "buy_token_with_usdc", lambda **kw: None)

    portfolio = Portfolio(
        user="0xabc",
        positions=[_make_position("USDC", 100.0, target_weight=1.0)],
    )

    rebalance(portfolio, router=cast(Any, object()))

    assert "withdraw_usdc" in calls
    assert "deposit_usdc" in calls


def test_rebalance_sells_overweight_tokens_before_buying_underweight(monkeypatch):
    trade_calls: list[str] = []
    monkeypatch.setattr(rebalance_module, "withdraw_usdc", lambda p: None)
    monkeypatch.setattr(rebalance_module, "deposit_usdc", lambda p: None)
    monkeypatch.setattr(rebalance_module, "sell_all", lambda *a, **kw: None)
    monkeypatch.setattr(
        rebalance_module,
        "sell_token_for_usdc",
        lambda **kw: trade_calls.append("sell"),
    )
    monkeypatch.setattr(
        rebalance_module,
        "buy_token_with_usdc",
        lambda **kw: trade_calls.append("buy"),
    )

    # WETH overweight (40% vs target 30%), WBTC underweight (20% vs target 30%)
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            _make_position("USDC", 40.0, target_weight=0.40),
            _make_position("WETH", 40.0, target_weight=0.30),   # +10% overweight → sell
            _make_position("WBTC", 20.0, target_weight=0.30),   # -10% underweight → buy
        ],
    )

    rebalance(portfolio, router=cast(Any, object()))

    assert trade_calls == ["sell", "buy"]


def test_rebalance_sells_all_when_target_weight_is_none(monkeypatch):
    sell_all_calls: list[str] = []
    monkeypatch.setattr(rebalance_module, "withdraw_usdc", lambda p: None)
    monkeypatch.setattr(rebalance_module, "deposit_usdc", lambda p: None)
    monkeypatch.setattr(
        rebalance_module,
        "sell_all",
        lambda router, portfolio, symbol: sell_all_calls.append(symbol),
    )
    monkeypatch.setattr(rebalance_module, "sell_token_for_usdc", lambda **kw: None)
    monkeypatch.setattr(rebalance_module, "buy_token_with_usdc", lambda **kw: None)

    # WETH has a balance but target_weight=None → should be fully liquidated
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            _make_position("USDC", 50.0, target_weight=1.0),
            _make_position("WETH", 50.0, target_weight=None),
        ],
    )

    rebalance(portfolio, router=cast(Any, object()))

    assert "WETH" in sell_all_calls

