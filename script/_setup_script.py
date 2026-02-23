from boa.contracts.vyper.vyper_contract import VyperContract
import boa
from boa.contracts.abi.abi_contract import ABIContract
from moccasin.config import get_active_network

STARTING_ETH_BALANCE = int(1000e18)  # 1000 ETH
STARTING_WETH_BALANCE = int(1e18)  # 1 wETH
STARTING_USDC_BALANCE = int(100e6)  # 100 USDC (6 decimals)
STARTING_WBTC_BALANCE = int(1e8)  # 1 WBTC (8 decimals)
STARTING_LINK_BALANCE = int(100e18)  # 100 LINK (18 decimals)
LINK_WHALE = "0xF977814e90dA44bFA03b6295A0616a897441aceC"


def _add_eth_balance() -> None:
    boa.env.set_balance(boa.env.eoa, STARTING_ETH_BALANCE)


def _add_token_balance(
    usdc: ABIContract, weth: ABIContract, wbtc: ABIContract, link: ABIContract
) -> None:
    weth.deposit(value=STARTING_WETH_BALANCE)

    our_address = boa.env.eoa
    with boa.env.prank(usdc.owner()):
        usdc.updateMasterMinter(our_address)
    usdc.configureMinter(our_address, STARTING_USDC_BALANCE)
    usdc.mint(our_address, STARTING_USDC_BALANCE)

    with boa.env.prank(wbtc.owner()):
        wbtc.mint(our_address, STARTING_WBTC_BALANCE)

    # For LINK, we'll transfer from a whale since minting is not possible.
    with boa.env.prank(LINK_WHALE):
        link.transfer(our_address, STARTING_LINK_BALANCE)


def setup_script() -> (ABIContract, ABIContract, ABIContract, ABIContract):
    print("Starting setup script...")

    # Give ourselves some ETH

    # Give ourselves some USDC, wETH, WBTC, and LINK
    active_network = get_active_network()

    usdc = active_network.manifest_named("usdc")
    weth = active_network.manifest_named("weth")
    wbtc = active_network.manifest_named("wbtc")
    link = active_network.manifest_named("link")

    if active_network.is_local_or_forked_network():
        _add_eth_balance()
        _add_token_balance(usdc, weth, wbtc, link)

    return (usdc, weth, wbtc, link)


def moccasin_main():
    (usdc, weth, wbtc, link) = setup_script()
    return (usdc, weth, wbtc, link)
