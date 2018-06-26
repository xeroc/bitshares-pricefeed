from bitshares_pricefeed.pricefeed import Feed

config = 'bitshares_pricefeed/examples/hero.yaml'

def test_hero_computation(conf, checkers):
    feed = Feed(conf)
    feed.derive({'HERO'})
    prices = feed.get_prices()
    checkers.check_price(prices, 'HERO', 'BTS', 0.1)
