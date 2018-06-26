import codecs
import re
import csv
import requests
from . import FeedSource, _request_headers


class Google(FeedSource):  # Google Finance
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = 60 * 60  # 1h
        self.days = 4

    def _adjustQuoteName(self, quote):
        if hasattr(self, "quoteNames") and quote in self.quoteNames:
            return self.quoteNames[quote]
        return quote

    def _fetch_one(self, ticker):
        url = (
            'http://www.google.com/finance/getprices'
            '?i={period}&p={days}d&f=d,c&df=cpct&q={ticker}'
        ).format(ticker=ticker, period=self.period, days=self.days)

        response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
        reader = csv.reader(codecs.iterdecode(response.content.splitlines(), "utf-8"))

        prices = []
        for row in reader:
            if re.match('^[a\d]', row[0]):
                prices.append(float(row[1]))

        return {"price": sum(prices) / len(prices),
                                "volume": 1.0}

    def _fetchForex(self, feed):
        for base in self.bases:
            feed[base] = {}

            for quote in self.quotes:
                if quote == base:
                    continue

                ticker = "%s%s" % (quote, base)
                feed[base][self._adjustQuoteName(quote)] = self._fetch_one(ticker)
        return feed

    def _fetchEquities(self, feed):
        if hasattr(self, "equities"):
            for equity in self.equities:
                    (quote, base) = equity.split(':')
                    if not base in feed:
                        feed[base] = {}
                    feed[base][self._adjustQuoteName(quote)] = self._fetch_one(quote)
        return feed

    def _fetch(self):
        feed = {}
        try:
            feed = self._fetchForex(feed)
            feed = self._fetchEquities(feed)
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        
        return feed

