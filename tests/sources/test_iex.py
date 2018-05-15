from bitshares_pricefeed.sources.iex import Iex

def test_iex_equities_fetch(checkers):
    source = Iex(equities=['F:USD', 'BABA:USD'], quoteNames={'F':'FORDCOM', 'BABA':'ALIBABACOM'}) 
    feed = source.fetch()
    checkers.check_feed(feed, ['FORDCOM:USD', 'ALIBABACOM:USD'])
