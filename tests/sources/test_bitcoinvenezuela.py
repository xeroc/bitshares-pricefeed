from bitshares_pricefeed.sources.bitcoinvenezuela import BitcoinVenezuela

def test_bitcoinvenezuela_fetch(checkers):
    source = BitcoinVenezuela(quotes=['BTC', 'EUR', 'USD'], bases=['BTC', 'EUR', 'USD']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTC:USD', 'BTC:EUR', 'USD:EUR'], noVolume=True)


