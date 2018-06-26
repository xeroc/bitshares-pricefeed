from bitshares_pricefeed.sources.manual import Manual

def test_manual_fetch(checkers):
    source = Manual(feed = { 'BTS' : { 'USD' : { 'price': 4.2, 'volume': 1.0}}}) 
    feed = source.fetch()
    checkers.check_feed(feed, ['USD:BTS'])
