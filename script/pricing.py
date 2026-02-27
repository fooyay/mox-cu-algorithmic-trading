from moccasin.config import Network, get_active_network
from dataclasses import replace
from script.tokens import TokenPosition


def get_price(symbol: str, network: Network | None = None) -> float:
    network = network or get_active_network()
    feed_name = f"{symbol.lower()}_usd_price_feed"
    price_feed = network.manifest_named(feed_name)

    raw_price: int = price_feed.latestRoundData()[1]
    # raw_price: int = price_feed.latestAnswer()
    decimals: int = 10 ** price_feed.decimals()
    price: float = raw_price / decimals
    return price


def update_prices(token_positions: list[TokenPosition], network: Network | None = None) -> list[TokenPosition]:
    network = network or get_active_network()
    updated_positions: list[TokenPosition] = []
    for token_position in token_positions:
        price: float = get_price(symbol=token_position.underlying_symbol, network=network)
        updated_positions.append(replace(token_position, recent_price=price))
    return updated_positions


def pricing_example():
    active_network: Network = get_active_network()
    print(f"Active network: {active_network.name}")
    eth_price = get_price(symbol="ETH", network=active_network)
    usdc_price = get_price(symbol="USDC", network=active_network)
    btc_price = get_price(symbol="BTC", network=active_network)
    link_price = get_price(symbol="LINK", network=active_network)
    print(f"ETH price: {eth_price}")
    print(f"USDC price: {usdc_price}")
    print(f"BTC price: {btc_price}")
    print(f"LINK price: {link_price}")


def moccasin_main():
    pricing_example()
