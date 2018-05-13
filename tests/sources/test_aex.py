from bitshares_pricefeed.sources.aex import Aex

def test_aex_fetch(checkers):
    source = Aex(quotes=['BTS'], bases=['BTC']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTS:BTC'])


