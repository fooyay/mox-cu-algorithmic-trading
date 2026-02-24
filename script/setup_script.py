import boa
from boa.contracts.abi.abi_contract import ABIContract
from moccasin.config import get_active_network
from script.aave import get_aave_pool_contract, deposit_in_pool, show_aave_statistics
from script.tokens import show_balances

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


def _deposit_into_aave_pool(tokens: list[ABIContract], network: str) -> ABIContract:
    pool_contract: ABIContract = get_aave_pool_contract(network)
    for token in tokens:
        balance: int = token.balanceOf(boa.env.eoa)
        if balance > 0:
            deposit_in_pool(pool_contract=pool_contract, token=token, amount=balance)
    return pool_contract


def setup_script(user: str) -> tuple[list[ABIContract], ABIContract]:
    print("Starting setup script...")

    active_network = get_active_network()

    usdc = active_network.manifest_named("usdc")
    weth = active_network.manifest_named("weth")
    wbtc = active_network.manifest_named("wbtc")
    link = active_network.manifest_named("link")

    tokens = [usdc, weth, wbtc, link]

    if active_network.is_local_or_forked_network():
        _add_eth_balance()
        _add_token_balance(usdc, weth, wbtc, link)
        show_balances(tokens=tokens, user=user)

        pool_contract: ABIContract = _deposit_into_aave_pool(
            tokens=tokens, network=active_network
        )
        show_aave_statistics(pool_contract=pool_contract, user=user)

    return tokens, pool_contract


def moccasin_main():
    (usdc, weth, wbtc, link) = setup_script()
    return (usdc, weth, wbtc, link)
