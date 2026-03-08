import boa
import pytest
from moccasin.config import get_active_network
from typing import Any, cast

from script.setup_script import (
    DESIRED_WEIGHTS,
    STARTING_ETH_BALANCE,
    STARTING_LINK_BALANCE,
    STARTING_USDC_BALANCE,
    STARTING_WBTC_BALANCE,
    STARTING_WETH_BALANCE,
    _add_token_balance,
    setup_script,
)
from script.aave import deposit_portfolio_into_aave, set_portfolio_pool_contract
from script.tokens import Portfolio, TokenPosition


def test_setup_script_returns_token_positions_for_expected_symbols():
    active_network = get_active_network()

    expected_usdc = active_network.manifest_named("usdc")
    expected_weth = active_network.manifest_named("weth")
    expected_wbtc = active_network.manifest_named("wbtc")
    expected_link = active_network.manifest_named("link")

    portfolio = setup_script()
    by_symbol = {
        token_position.symbol: token_position for token_position in portfolio.positions
    }

    assert set(by_symbol.keys()) == {"USDC", "WETH", "WBTC", "LINK"}
    assert by_symbol["USDC"].token.address == expected_usdc.address
    assert by_symbol["WETH"].token.address == expected_weth.address
    assert by_symbol["WBTC"].token.address == expected_wbtc.address
    assert by_symbol["LINK"].token.address == expected_link.address


def test_setup_script_returns_token_positions_with_matching_a_tokens_on_local_or_forked_network():
    active_network = get_active_network()

    portfolio = setup_script()

    if active_network.is_local_or_forked_network():
        assert all(
            token_position.a_token is not None for token_position in portfolio.positions
        )
    else:
        assert all(
            isinstance(token_position.a_token, type(None))
            or token_position.a_token.address
            for token_position in portfolio.positions
        )


def test_setup_script_returns_portfolio_of_token_positions():
    portfolio = setup_script()

    assert isinstance(portfolio, Portfolio)
    assert portfolio.positions
    assert all(
        isinstance(token_position, TokenPosition)
        for token_position in portfolio.positions
    )
    assert all(
        token_position.recent_price is not None
        for token_position in portfolio.positions
    )
    assert all(
        token_position.target_weight == DESIRED_WEIGHTS.get(token_position.symbol)
        for token_position in portfolio.positions
    )


def test_add_token_balance_sets_expected_balances_for_each_token():
    active_network = get_active_network()
    if not active_network.is_local_or_forked_network():
        pytest.skip("_add_token_balance test requires a local or forked network")

    user = boa.env.eoa
    boa.env.set_balance(user, STARTING_ETH_BALANCE)

    usdc: Any = active_network.manifest_named("usdc")
    weth: Any = active_network.manifest_named("weth")
    wbtc: Any = active_network.manifest_named("wbtc")
    link: Any = active_network.manifest_named("link")

    before_usdc = usdc.balanceOf(user)
    before_weth = weth.balanceOf(user)
    before_wbtc = wbtc.balanceOf(user)
    before_link = link.balanceOf(user)

    _add_token_balance(usdc=usdc, weth=weth, wbtc=wbtc, link=link)

    assert usdc.balanceOf(user) - before_usdc == STARTING_USDC_BALANCE
    assert weth.balanceOf(user) - before_weth == STARTING_WETH_BALANCE
    assert wbtc.balanceOf(user) - before_wbtc == STARTING_WBTC_BALANCE
    assert link.balanceOf(user) - before_link == STARTING_LINK_BALANCE


def test_deposit_portfolio_into_aave_deposits_only_positive_balances(monkeypatch):
    class DummyToken:
        def __init__(self, symbol: str, balance: int):
            self.symbol = symbol
            self._balance = balance
            self.address = f"0x{symbol}"

        def balanceOf(self, _user: str) -> int:
            return self._balance

    class DummyPool:
        address = "0xpool"

    usdc = cast(Any, DummyToken("USDC", 100))
    weth = cast(Any, DummyToken("WETH", 0))
    token = cast(Any, object())
    portfolio = Portfolio(
        user="0xabc",
        positions=[
            TokenPosition(
                symbol="USDC",
                underlying_symbol="USDC",
                token=usdc,
                a_token=token,
            ),
            TokenPosition(
                symbol="WETH",
                underlying_symbol="WETH",
                token=weth,
                a_token=token,
            ),
        ],
    )

    calls: list[tuple[Any, Any, int]] = []

    monkeypatch.setattr("script.aave._resolve_pool_contract", lambda: DummyPool())

    portfolio = set_portfolio_pool_contract(portfolio)
    assert portfolio.pool_contract.address == "0xpool"

    monkeypatch.setattr(
        "script.aave.deposit_in_pool",
        lambda pool_contract, token, amount: calls.append((pool_contract, token, amount)),
    )

    deposit_portfolio_into_aave(portfolio)

    assert len(calls) == 1
    assert calls[0][0].address == "0xpool"
    assert calls[0][1].address == "0xUSDC"
    assert calls[0][2] == 100
