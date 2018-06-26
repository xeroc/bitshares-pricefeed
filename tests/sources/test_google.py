from bitshares_pricefeed.sources.google import Google

def test_google_forex_fetch(checkers):
    source = Google(quotes=['EUR', 'USD', 'CNY'], bases=['USD', 'CNY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['EUR:USD', 'CNY:USD', 'EUR:CNY', 'USD:CNY'], noVolume=True)

def test_google_equities_fetch(checkers):
    source = Google(equities=['F:USD', 'BABA:USD'], quoteNames={'F':'FORDCOM', 'BABA':'ALIBABACOM'}) 
    feed = source.fetch()
    checkers.check_feed(feed, ['FORDCOM:USD', 'ALIBABACOM:USD'], noVolume=True)

def test_google_multiple_equities_fetch(checkers):    
    source = Google(quotes=['EUR'], bases=['USD'], equities=['F:USD', 'BABA:USD']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['EUR:USD', 'F:USD', 'BABA:USD'], noVolume=True)

