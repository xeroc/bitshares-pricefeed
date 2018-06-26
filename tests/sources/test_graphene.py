from bitshares_pricefeed.sources.graphene import Graphene

def test_graphene_fetch(checkers):
    source = Graphene(quotes=['USD', 'CNY'], bases=['BTS']) 
    feed = source.fetch()
    checkers.check_feed(feed, ['USD:BTS', 'CNY:BTS'])


