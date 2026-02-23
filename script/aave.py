import boa
from boa.contracts.abi.abi_contract import ABIContract
from moccasin.config import Network


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


def deposit(pool_contract, token, amount):
    allowed_amount = token.allowance(boa.env.eoa, pool_contract.address)
    if allowed_amount < amount:
        token.approve(pool_contract.address, amount)
    print(
        f"Depositing {amount} of token {token.name()} to Aave Pool {pool_contract.address}..."
    )
    pool_contract.supply(token.address, amount, boa.env.eoa, REFERRAL_CODE)
