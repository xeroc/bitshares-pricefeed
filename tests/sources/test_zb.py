from bitshares_pricefeed.sources.zb import Zb

def test_zb_fetch(checkers):
    source = Zb(quotes=['BTS', 'ETH'], bases=['BTC']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTS:BTC', 'ETH:BTC'])


