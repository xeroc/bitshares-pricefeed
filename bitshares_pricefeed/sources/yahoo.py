import csv
import json
import requests
from . import FeedSource, _request_headers


class Yahoo(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            # Currencies and commodities
            for base in self.bases:
                feed[base] = {}
                yahooAssets = ",".join([a + base + "=X" for a in self.quotes])
                url = "http://download.finance.yahoo.com/d/quotes.csv"
                params = {'s': yahooAssets, 'f': 'l1', 'e': '.csv'}
                response = requests.get(url=url, headers=_request_headers, timeout=self.timeout, params=params)
                yahooprices = response.text.replace('\r', '').split('\n')
                for i, quote in enumerate(self.quotes):
                    if float(yahooprices[i]) > 0:
                        if hasattr(self, "quoteNames") and quote in self.quoteNames:
                            quote = self.quoteNames[quote]
                        feed[base][quote] = {"price": (float(yahooprices[i])),
                                             "volume": 1.0}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
