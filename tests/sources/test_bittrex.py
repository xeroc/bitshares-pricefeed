from bitshares_pricefeed.sources.bittrex import Bittrex

def test_bittrex_fetch(checkers):
    source = Bittrex(quotes=['BTC'], bases=['USDT'], quoteNames='USDT:USD') 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTC:USDT'])


