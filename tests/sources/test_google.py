from bitshares_pricefeed.sources.google import Google

def test_google_fetch():
    source = Google(quotes=['EUR'], bases=['USD'], equities=['F:USD'], quoteNames={'F':'FORDCOM'}) 
    feed = source.fetch()
    print(feed)
    assert 'USD' in feed
    for q in ['EUR', 'FORDCOM']:
        assert q in feed['USD']
        for f in ['volume', 'price']:
            assert f in feed['USD'][q]
        assert feed['USD'][q]['volume'] == 1.0 


