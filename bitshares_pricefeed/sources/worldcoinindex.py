import requests
from . import FeedSource, _request_headers

class WorldCoinIndex(FeedSource):  # Weighted average from WorldCoinIndex 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = getattr(self, 'timeout', 15)
        if not hasattr(self, 'api_key'):
            raise Exception("WorldCoinIndex FeedSource requires 'api_key'.")

    def _adjustQuoteName(self, quote):
        if hasattr(self, 'quoteNames') and quote in self.quoteNames:
            return self.quoteNames[quote]
        return quote

    def _fetch(self):
        feed = {}
        try:
            for base in self.bases:
                url = "https://www.worldcoinindex.com/apiservice/v2getmarkets?key={apikey}&fiat={base}"
                response = requests.get(url=url.format(apikey=self.api_key, base=base),
                                        headers=_request_headers, timeout=self.timeout)
                result = response.json()['Markets']
                feed[base] = {}
                for market in result:
                    for ticker in market:
                        (quote, returnedBase) = ticker['Label'].split('/')
                        if base == returnedBase and quote in self.quotes:
                            feed[base][self._adjustQuoteName(quote)] = {
                                "price": ticker['Price'],
                                "volume": ticker['Volume_24h'] * self.scaleVolumeBy}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
