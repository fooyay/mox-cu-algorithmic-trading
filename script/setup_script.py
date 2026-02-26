import boa
from boa.contracts.abi.abi_contract import ABIContract
from moccasin.config import get_active_network
from script.aave import get_aave_pool_contract, deposit_in_pool, show_aave_statistics
from script.tokens import show_balances, TokenPosition, show_aave_positions

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


def _get_token_positions(tokens: list[ABIContract]) -> list[TokenPosition]:
    active_network = get_active_network()
    aave_protocol_data_provider = active_network.manifest_named(
        "aave_protocol_data_provider"
    )
    a_tokens = aave_protocol_data_provider.getAllATokens()

    token_positions: list[TokenPosition] = []
    for token in tokens:
        symbol = token.symbol().upper()
        token_manifest_name = symbol.lower()
        matching_a_token_address = None
        for a_token_symbol, a_token_address in a_tokens:
            if symbol in a_token_symbol:
                matching_a_token_address = a_token_address
                break

        a_token_contract: ABIContract | None = None
        if matching_a_token_address:
            a_token_contract = active_network.manifest_named(
                token_manifest_name, address=matching_a_token_address
            )
        underlying_symbol = symbol[1:] if symbol in ["WETH", "WBTC"] else symbol

        token_positions.append(
            TokenPosition(
                symbol=symbol,
                underlying_symbol=underlying_symbol,
                token=token,
                a_token=a_token_contract,
            )
        )

    return token_positions


def setup_script(user: str) -> tuple[list[TokenPosition], ABIContract]:
    print("Starting setup script...")

    active_network = get_active_network()

    usdc = active_network.manifest_named("usdc")
    weth = active_network.manifest_named("weth")
    wbtc = active_network.manifest_named("wbtc")
    link = active_network.manifest_named("link")

    tokens = [usdc, weth, wbtc, link]

    pool_contract = get_aave_pool_contract(active_network)
    if active_network.is_local_or_forked_network():
        _add_eth_balance()
        _add_token_balance(usdc, weth, wbtc, link)
        show_balances(tokens=tokens, user=user)

        pool_contract = _deposit_into_aave_pool(tokens=tokens, network=active_network)
        show_aave_statistics(pool_contract=pool_contract, user=user)

    token_positions = _get_token_positions(tokens=tokens)

    show_aave_positions(token_positions=token_positions, user=user)
    return token_positions, pool_contract


def moccasin_main():
    (token_positions, _pool_contract) = setup_script(user=boa.env.eoa)
    return token_positions
