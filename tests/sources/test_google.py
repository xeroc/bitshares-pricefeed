from bitshares_pricefeed.sources.google import Google

def test_google_fetch(checkers):
    source = Google(quotes=['EUR'], bases=['USD'], equities=['F:USD'], quoteNames={'F':'FORDCOM'}) 
    feed = source.fetch()
    quotes = ['EUR', 'FORDCOM']
    checkers.check_feed(feed, quotes, ['USD'])
    for q in quotes:
        assert feed['USD'][q]['volume'] == 1.0 


