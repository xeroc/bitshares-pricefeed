import requests
from . import FeedSource, _request_headers

class AlphaVantage(FeedSource):  # Alpha Vantage
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = getattr(self, 'timeout', 15)
        if not hasattr(self, "api_key"):
            raise Exception("AlphaVantage FeedSource requires an 'api_key'.")


    def _adjustQuoteName(self, quote):
        if hasattr(self, "quoteNames") and quote in self.quoteNames:
            quote = self.quoteNames[quote]
        return quote

    def _fetchForex(self, feed):
        for base in self.bases:
            if not base in feed:
                feed[base] = {}
            for quote in self.quotes:
                if quote == base:
                    continue
                ticker = "%s%s" % (quote, base)
                url = (
                    'https://www.alphavantage.co/query'
                    '?function=CURRENCY_EXCHANGE_RATE&from_currency={quote}&to_currency={base}&apikey={apikey}'
                ).format(base=base, quote=quote, apikey=self.api_key)
                response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                result = response.json()
                price = float(result['Realtime Currency Exchange Rate']['5. Exchange Rate'])
                feed[base][self._adjustQuoteName(quote)] = {"price": price, "volume": 1.0}
        return feed


    def _fetchEquities(self, feed):
        if not hasattr(self, "equities") or len(self.equities) == 0:
            return feed

        symbols = ",".join([ equity.split(':')[0] for equity in self.equities ])
        url = (
            'https://www.alphavantage.co/query'
            '?function=BATCH_STOCK_QUOTES&symbols={symbols}&apikey={apikey}'
        ).format(symbols=symbols, apikey=self.api_key)

        response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
        result = response.json()
        print(result)

        for equity in self.equities:
            (name, base) = equity.split(':')
            if not base in feed:
                feed[base] = {}
            for ticker in result['Stock Quotes']:
                if ticker['1. symbol'] == name:
                    volume = 1.0
                    if ticker['3. volume'] != '--':
                        volume = float(ticker['3. volume']) * self.scaleVolumeBy
                    feed[base][self._adjustQuoteName(name)] = { "price": float(ticker['2. price']),
                                                                "volume": volume }
        return feed


    def _fetch(self):
        feed = {}
        try:
            feed = self._fetchForex(feed)
            feed = self._fetchEquities(feed)
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
