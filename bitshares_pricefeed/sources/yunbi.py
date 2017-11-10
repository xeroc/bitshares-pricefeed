import csv
import json
import requests
from . import FeedSource, _request_headers


class Yunbi(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            url = "https://yunbi.com/api/v2/tickers.json"
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()
            feed["response"] = result
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if quote == base:
                        continue
                    marketName = quote.lower() + base.lower()
                    if hasattr(self, "quoteNames") and quote in self.quoteNames:
                        quote = self.quoteNames[quote]
                    if marketName in result:
                        if hasattr(self, "quoteNames") and quote in self.quoteNames:
                            quote = self.quoteNames[quote]
                        feed[base][quote] = {"price": (float(result[marketName]["ticker"]["last"])),
                                             "volume": (float(result[marketName]["ticker"]["vol"]) * self.scaleVolumeBy)}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
