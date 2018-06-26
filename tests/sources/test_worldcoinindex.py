from bitshares_pricefeed.sources.worldcoinindex import WorldCoinIndex
import os

def test_worldcoinindex_fetch(checkers):
    source = WorldCoinIndex(quotes=['BTC', 'BTS'], bases=['BTC', 'USD'], api_key=os.environ['WORLDCOININDEX_APIKEY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTC:USD', 'BTS:BTC', 'BTS:USD'])


