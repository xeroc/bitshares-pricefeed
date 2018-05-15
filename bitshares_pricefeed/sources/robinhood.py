import json
import requests
from . import FeedSource, _request_headers

class RobinHood(FeedSource): # Stocks prices from RobinHood: https://github.com/sanko/Robinhood
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _adjustQuoteName(self, quote):
        if hasattr(self, "quoteNames") and quote in self.quoteNames:
            return self.quoteNames[quote]
        return quote

    def _extract_symbols(self):
        symbols_by_base = {}
        for equity in self.equities:
            (symbol, base) = equity.split(':')
            if base not in symbols_by_base:
                symbols_by_base[base] = []
            symbols_by_base[base].append(symbol)
        return symbols_by_base

    def _fetch(self):
        symbols_by_base = self._extract_symbols()
        feed = {}
        try:
            url = "https://api.robinhood.com/quotes/?symbols={symbols}"
            for base in symbols_by_base.keys():
                response = requests.get(url=url.format(
                    symbols=','.join(symbols_by_base[base])
                ), headers=_request_headers, timeout=self.timeout)
                result = response.json()['results']
                feed[base] = {}
                for ticker in result:
                    feed[base][self._adjustQuoteName(ticker['symbol'])] = { 
                        "price": float(ticker["last_trade_price"]),
                        "volume": 1.0
                    }
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed