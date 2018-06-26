from bitshares_pricefeed.sources.chbtc import ChBTC

def test_chbtc_fetch(checkers):
    source = ChBTC(quotes=['BTC'], bases=['CNY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTC:CNY'])


