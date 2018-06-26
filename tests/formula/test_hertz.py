from bitshares_pricefeed.pricefeed import Feed

config = 'bitshares_pricefeed/examples/hertz.yaml'

def test_hertz_computation(conf, checkers):
    feed = Feed(conf)
    feed.derive({'HERTZ'})
    prices = feed.get_prices()
    checkers.check_price(prices, 'HERTZ', 'BTS', 0.1)
