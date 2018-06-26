from bitshares_pricefeed.sources.currencylayer import CurrencyLayer
import os

def test_currencylayer_fetch(checkers):
    source = CurrencyLayer(quotes=['BTC', 'EUR'], bases=['USD'], api_key=os.environ['CURRENCYLAYER_APIKEY'], free_subscription=True) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTC:USD', 'EUR:USD'], noVolume=True)


