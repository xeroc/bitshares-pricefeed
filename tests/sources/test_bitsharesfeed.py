from bitshares_pricefeed.sources.bitsharesfeed import BitsharesFeed

def test_bitsharesfeed_fetch(checkers):
    source = BitsharesFeed(assets=['USD', 'CNY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTS:USD', 'BTS:CNY'], noVolume=True)


