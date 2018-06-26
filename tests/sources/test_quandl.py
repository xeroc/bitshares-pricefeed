from bitshares_pricefeed.sources.quandl import Quandl, QuandlPlain
import os

def test_quandl_fetch(checkers):
    source = Quandl(datasets = {'GOLD:USD' : ['LBMA/GOLD'], 'SILVER:USD': ['LBMA/SILVER']}, api_key=os.environ['QUANDL_APIKEY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['GOLD:USD', 'SILVER:USD'], noVolume=True)

def test_quandl_plain_fetch(checkers):
    source = QuandlPlain(datasets = {'GOLD:USD' : ['LBMA/GOLD'], 'SILVER:USD': ['LBMA/SILVER']}, api_key=os.environ['QUANDL_APIKEY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['GOLD:USD', 'SILVER:USD'], noVolume=True)


