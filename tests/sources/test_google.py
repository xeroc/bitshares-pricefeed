from bitshares_pricefeed.sources.google import Google

def test_google_fetch(checkers):
    source = Google(quotes=['EUR'], bases=['USD'], equities=['F:USD'], quoteNames={'F':'FORDCOM'}) 
    feed = source.fetch()
    checkers.check_feed(feed, ['EUR:USD', 'FORDCOM:USD'], noVolume=True)


