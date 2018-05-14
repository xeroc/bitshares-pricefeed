from bitshares_pricefeed.sources.openexchangerate import OpenExchangeRates
import os

def test_openexchangerates_fetch(checkers):
    source = OpenExchangeRates(quotes=['BTC', 'EUR'], bases=['USD'], 
                               api_key=os.environ['OPENEXCHANGERATE_APIKEY'], free_subscription=True) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTC:USD', 'EUR:USD'], noVolume=True)


