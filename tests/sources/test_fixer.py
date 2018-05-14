from bitshares_pricefeed.sources.fixer import Fixer
import os

def test_fixer_fetch(checkers):
    source = Fixer(quotes=['CNY', 'USD'], bases=['USD', 'EUR'], api_key=os.environ['FIXER_APIKEY'], free_subscription=True) 
    feed = source.fetch()
    checkers.check_feed(feed, ['CNY:EUR', 'USD:EUR'], noVolume=True)


