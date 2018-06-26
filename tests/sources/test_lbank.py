from bitshares_pricefeed.sources.lbank import Lbank

def test_lbank_fetch(checkers):
    source = Lbank(quotes=['BTS', 'ETH'], bases=['BTC']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTS:BTC', 'ETH:BTC'])


