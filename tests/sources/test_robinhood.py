from bitshares_pricefeed.sources.robinhood import RobinHood

def test_robinhood_equities_fetch(checkers):
    source = RobinHood(equities=['F:USD', 'BABA:USD'], quoteNames={'F':'FORDCOM', 'BABA':'ALIBABACOM'}) 
    feed = source.fetch()
    checkers.check_feed(feed, ['FORDCOM:USD', 'ALIBABACOM:USD'], noVolume=True)
