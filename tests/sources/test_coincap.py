from bitshares_pricefeed.sources.coincap import Coincap

def test_coincap_fetch(checkers):
    source = Coincap(quotes=['ALTCAP', 'ALTCAP.X'], bases=['BTC']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['ALTCAP:BTC', 'ALTCAP.X:BTC'], noVolume=True)


