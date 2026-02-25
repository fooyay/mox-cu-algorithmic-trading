import boa
import pytest
from moccasin.config import get_active_network
from typing import Any

from script.setup_script import (
    STARTING_ETH_BALANCE,
    STARTING_LINK_BALANCE,
    STARTING_USDC_BALANCE,
    STARTING_WBTC_BALANCE,
    STARTING_WETH_BALANCE,
    TokenPosition,
    _add_token_balance,
    setup_script,
)


def test_setup_script_returns_token_positions_for_expected_symbols():
    active_network = get_active_network()
    user = boa.env.eoa

    expected_usdc = active_network.manifest_named("usdc")
    expected_weth = active_network.manifest_named("weth")
    expected_wbtc = active_network.manifest_named("wbtc")
    expected_link = active_network.manifest_named("link")

    token_positions, _pool_contract = setup_script(user=user)
    by_symbol = {
        token_position.symbol: token_position for token_position in token_positions
    }

    assert set(by_symbol.keys()) == {"USDC", "WETH", "WBTC", "LINK"}
    assert by_symbol["USDC"].token.address == expected_usdc.address
    assert by_symbol["WETH"].token.address == expected_weth.address
    assert by_symbol["WBTC"].token.address == expected_wbtc.address
    assert by_symbol["LINK"].token.address == expected_link.address


def test_setup_script_returns_token_positions_with_matching_a_tokens_on_local_or_forked_network():
    active_network = get_active_network()
    user = boa.env.eoa

    token_positions, _pool_contract = setup_script(user=user)

    if active_network.is_local_or_forked_network():
        assert all(
            token_position.a_token is not None for token_position in token_positions
        )
    else:
        assert all(
            isinstance(token_position.a_token, type(None))
            or token_position.a_token.address
            for token_position in token_positions
        )


def test_setup_script_returns_token_position_objects():
    user = boa.env.eoa

    token_positions, _pool_contract = setup_script(user=user)

    assert token_positions
    assert all(
        isinstance(token_position, TokenPosition) for token_position in token_positions
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
