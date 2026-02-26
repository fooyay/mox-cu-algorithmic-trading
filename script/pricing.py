from moccasin.config import Network, get_active_network


def get_price(network: Network, symbol: str) -> float:
    feed_name = f"{symbol.lower()}_usd_price_feed"
    price_feed = network.manifest_named(feed_name)

    raw_price: int = price_feed.latestRoundData()[1]
    # raw_price: int = price_feed.latestAnswer()
    decimals: int = 10 ** price_feed.decimals()
    price: float = raw_price / decimals
    return price


def pricing_example():
    active_network: Network = get_active_network()
    print(f"Active network: {active_network.name}")
    eth_price = get_price(network=active_network, symbol="ETH")
    usdc_price = get_price(network=active_network, symbol="USDC")
    btc_price = get_price(network=active_network, symbol="BTC")
    link_price = get_price(network=active_network, symbol="LINK")
    print(f"ETH price: {eth_price}")
    print(f"USDC price: {usdc_price}")
    print(f"BTC price: {btc_price}")
    print(f"LINK price: {link_price}")


def moccasin_main():
    pricing_example()
