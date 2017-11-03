import codecs
import re
import csv
import json
import requests
import datetime
from . import FeedSource, _request_headers


class Google(FeedSource):  # Google Finance
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = 60 * 60  # 1h
        self.days = 4

    def _fetch(self):
        feed = {}
        try:
            for base in self.bases:
                feed[base] = {}

                for quote in self.quotes:
                    if quote == base:
                        continue

                    ticker = "%s%s" % (quote, base)
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

                    if hasattr(self, "quoteNames") and quote in self.quoteNames:
                        quote = self.quoteNames[quote]
                    feed[base][quote] = {"price": sum(prices) / len(prices),
                                         "volume": 1.0}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
