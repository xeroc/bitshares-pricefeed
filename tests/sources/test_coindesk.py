from bitshares_pricefeed.sources.coindesk import Coindesk

def test_coindesk_fetch(checkers):
    source = Coindesk(quotes=['BTC'], bases=['USD', 'CNY']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTC:USD', 'BTC:CNY'])
