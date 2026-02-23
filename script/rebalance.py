from boa.contracts.abi.abi_contract import ABIContract
import boa
from moccasin.config import get_active_network, Network
from script._setup_script import setup_script
from script.aave import get_aave_pool_contract, deposit_in_pool
from script.tokens import show_balances


def rebalance_example():
    active_network: Network = get_active_network()

    # We're only going to play with eth-forked (the default).
    print(f"Active network: {active_network.name}")

    user: str = boa.env.eoa
    # usdc, weth, wbtc, wsol
    tokens: list[ABIContract] = setup_script()
    show_balances(tokens=tokens, user=user)

    pool_contract = get_aave_pool_contract(active_network)

    for token in tokens:
        balance = token.balanceOf(user)
        if balance > 0:
            deposit_in_pool(pool_contract=pool_contract, token=token, amount=balance)

    (
        totalCollateralBase,
        totalDebtBase,
        availableBorrowBase,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = pool_contract.getUserAccountData(boa.env.eoa)
    print(f"""User account data:
        totalCollateralBase: {totalCollateralBase}
        totalDebtBase: {totalDebtBase}
        availableBorrowBase: {availableBorrowBase}
        currentLiquidationThreshold: {currentLiquidationThreshold}
        ltv: {ltv}
        healthFactor: {healthFactor}
    """)


def moccasin_main():

    rebalance_example()
