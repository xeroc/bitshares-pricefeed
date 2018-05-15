from bitshares_pricefeed.sources.binance import Binance

def test_binance_fetch(checkers):
    source = Binance(quotes=['BTS', 'ETH'], bases=['BTC', 'USDT'], quoteNames={'USDT':'USD'}) 
    feed = source.fetch()
    checkers.check_feed(feed, ['BTS:BTC', 'ETH:BTC', 'ETH:USDT'])


