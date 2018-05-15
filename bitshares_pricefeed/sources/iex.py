import json
import requests
from . import FeedSource, _request_headers

class Iex(FeedSource): # Stocks prices from iextrading.com
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
            url = "https://api.iextrading.com/1.0/stock/market/batch?symbols={symbols}&types=quote"
            for base in symbols_by_base.keys():
                response = requests.get(url=url.format(
                    symbols=','.join(symbols_by_base[base])
                ), headers=_request_headers, timeout=self.timeout)
                result = response.json()
                feed[base] = {}
                for symbol in result.keys():
                    ticker = result[symbol]['quote']
                    feed[base][self._adjustQuoteName(symbol)] = { 
                        "price": (float(ticker["latestPrice"])),
                        "volume": (float(ticker["latestVolume"])* self.scaleVolumeBy)
                    }
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed