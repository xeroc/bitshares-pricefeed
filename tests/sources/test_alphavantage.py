from bitshares_pricefeed.sources.alphavantage import AlphaVantage
import os

def test_alphavantage_forex_fetch(checkers):
    source = AlphaVantage(quotes=['EUR'], bases=['USD'], api_key=os.environ['ALPHAVANTAGE_APIKEY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['EUR:USD'], noVolume=True)

def test_alphavantage_equities_fetch(checkers):
    source = AlphaVantage(equities=['F:USD', 'BABA:USD'], quoteNames={'F':'FORDCOM', 'BABA':'ALIBABACOM'},
                          api_key=os.environ['ALPHAVANTAGE_APIKEY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['FORDCOM:USD', 'ALIBABACOM:USD'])

def test_alphavantage_full_fetch(checkers):    
    source = AlphaVantage(quotes=['EUR'], bases=['USD'], equities=['F:USD', 'BABA:USD'],
                          api_key=os.environ['ALPHAVANTAGE_APIKEY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['EUR:USD', 'F:USD', 'BABA:USD'])