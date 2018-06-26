from bitshares_pricefeed.pricefeed import Feed

config = 'bitshares_pricefeed/examples/XCD.yaml'

def test_XCD_computation(conf, checkers):
    feed = Feed(conf)
    feed.derive({'XCD'})
    prices = feed.get_prices()
    checkers.check_price(prices, 'XCD', 'USD', 0.1)
