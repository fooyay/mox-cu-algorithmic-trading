import boa
from dataclasses import replace
from boa.contracts.abi.abi_contract import ABIContract
from moccasin.config import Network, get_active_network

from script.tokens import Portfolio


REFERRAL_CODE = 0


def get_aave_pool_contract(active_network: Network) -> ABIContract:
    aave_pool_address_provider = active_network.manifest_named(
        "aave_pool_address_provider"
    )
    pool_address = aave_pool_address_provider.getPool()

    pool_contract: ABIContract = active_network.manifest_named(
        "pool", address=pool_address
    )
    return pool_contract


def deposit_in_pool(pool_contract, token, amount) -> None:
    allowed_amount = token.allowance(boa.env.eoa, pool_contract.address)
    if allowed_amount < amount:
        token.approve(pool_contract.address, amount)
    # print(
    #     f"Depositing {amount} of token {token.name()} to Aave Pool {pool_contract.address}..."
    # )
    pool_contract.supply(token.address, amount, boa.env.eoa, REFERRAL_CODE)


def show_aave_statistics(pool_contract: ABIContract, user: str) -> None:
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


def _resolve_pool_contract(active_network: Network | None = None) -> ABIContract:
    network = active_network or get_active_network()
    return get_aave_pool_contract(network)


def _deposit_tokens_into_pool(
    tokens: list[ABIContract], pool_contract: ABIContract, user: str
) -> None:
    for token in tokens:
        balance: int = token.balanceOf(user)
        if balance > 0:
            deposit_in_pool(pool_contract=pool_contract, token=token, amount=balance)


def set_portfolio_pool_contract(portfolio: Portfolio) -> Portfolio:
    pool_contract = _resolve_pool_contract()
    return replace(portfolio, pool_contract=pool_contract)


def deposit_portfolio_into_aave(portfolio: Portfolio) -> None:
    tokens = [token_position.token for token_position in portfolio.positions]
    _deposit_tokens_into_pool(
        tokens=tokens,
        pool_contract=portfolio.pool_contract,
        user=portfolio.user,
    )


def withdraw_usdc(portfolio: Portfolio) -> None:
    """Withdraw the full aUSDC balance from Aave back to the user wallet."""
    usdc_position = portfolio.by_symbol["USDC"]
    a_token_balance: int = usdc_position.a_token.balanceOf(portfolio.user)
    if a_token_balance > 0:
        portfolio.pool_contract.withdraw(
            usdc_position.token.address, a_token_balance, portfolio.user
        )


def deposit_usdc(portfolio: Portfolio) -> None:
    """Deposit the full USDC wallet balance into Aave."""
    usdc_position = portfolio.by_symbol["USDC"]
    balance: int = usdc_position.token.balanceOf(portfolio.user)
    if balance > 0:
        deposit_in_pool(
            pool_contract=portfolio.pool_contract,
            token=usdc_position.token,
            amount=balance,
        )
