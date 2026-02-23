import boa
from moccasin.config import get_active_network

from script._setup_script import (
    STARTING_ETH_BALANCE,
    STARTING_USDC_BALANCE,
    STARTING_WBTC_BALANCE,
    STARTING_WETH_BALANCE,
    STARTING_WSOL_BALANCE,
    setup_script,
)


def test_setup_script_returns_expected_token_contracts():
    active_network = get_active_network()

    expected_usdc = active_network.manifest_named("usdc")
    expected_weth = active_network.manifest_named("weth")
    expected_wbtc = active_network.manifest_named("wbtc")
    expected_wsol = active_network.manifest_named("wsol")

    usdc, weth, wbtc, wsol = setup_script()

    assert usdc.address == expected_usdc.address
    assert weth.address == expected_weth.address
    assert wbtc.address == expected_wbtc.address
    assert wsol.address == expected_wsol.address


def test_setup_script_sets_starting_balances_on_local_or_forked_network():
    active_network = get_active_network()
    user = boa.env.eoa

    usdc = active_network.manifest_named("usdc")
    weth = active_network.manifest_named("weth")
    wbtc = active_network.manifest_named("wbtc")
    wsol = active_network.manifest_named("wsol")

    before_eth = boa.env.get_balance(user)
    before_usdc = usdc.balanceOf(user)
    before_weth = weth.balanceOf(user)
    before_wbtc = wbtc.balanceOf(user)
    before_wsol = wsol.balanceOf(user)

    setup_script()

    if active_network.is_local_or_forked_network():
        after_eth = boa.env.get_balance(user)
        assert STARTING_ETH_BALANCE - int(1e18) <= after_eth <= STARTING_ETH_BALANCE
        assert usdc.balanceOf(user) - before_usdc == STARTING_USDC_BALANCE
        assert weth.balanceOf(user) - before_weth == STARTING_WETH_BALANCE
        assert wbtc.balanceOf(user) - before_wbtc == STARTING_WBTC_BALANCE
        assert wsol.balanceOf(user) - before_wsol == STARTING_WSOL_BALANCE
    else:
        assert boa.env.get_balance(user) == before_eth
        assert usdc.balanceOf(user) == before_usdc
        assert weth.balanceOf(user) == before_weth
        assert wbtc.balanceOf(user) == before_wbtc
        assert wsol.balanceOf(user) == before_wsol
