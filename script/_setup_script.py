import boa
from boa.contracts.abi.abi_contract import ABIContract
from moccasin.config import get_active_network, Network

STARTING_ETH_BALANCE = int(1000e18)  # 1000 ETH
STARTING_WETH_BALANCE = int(1e18)  # 1 wETH
STARTING_USDC_BALANCE = int(100e6)  # 100 USDC (6 decimals)


def _add_eth_balance() -> None:
    boa.env.set_balance(boa.env.eoa, STARTING_ETH_BALANCE)


def _add_token_balance(
    usdc: ABIContract, weth: ABIContract, active_network: Network
) -> None:
    weth.deposit(value=STARTING_WETH_BALANCE)

    our_address = boa.env.eoa
    with boa.env.prank(usdc.owner()):
        usdc.updateMasterMinter(our_address)
    usdc.configureMinter(our_address, STARTING_USDC_BALANCE)
    usdc.mint(our_address, STARTING_USDC_BALANCE)
    print(f"USDC balance after: {usdc.balanceOf(our_address)}")


def setup_script() -> (ABIContract, ABIContract, ABIContract, ABIContract):
    print("Starting setup script...")

    # Give ourselves some ETH

    # Give ourselves some USDC and wETH
    active_network = get_active_network()

    usdc = active_network.manifest_named("usdc")
    weth = active_network.manifest_named("weth")

    if active_network.is_local_or_forked_network():
        _add_eth_balance()
        _add_token_balance(usdc, weth, active_network)

    return (usdc, weth)


def moccasin_main():
    (usdc, weth) = setup_script()
    return (usdc, weth)
