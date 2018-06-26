from bitshares_pricefeed.sources.bitstamp import Bitstamp

def test_bitstamp_fetch(checkers):
    source = Bitstamp(quotes=['BTC'], bases=['USD', 'EUR']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTC:USD', 'BTC:EUR'])


