import csv
import json
import requests
from . import FeedSource, _request_headers


class Bter(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            url = "http://data.bter.com/api/1/tickers"
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()
            feed["response"] = result
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if quote == base:
                        continue
                    if quote.lower() + "_" + base.lower() in result:
                        if hasattr(self, "quoteNames") and quote in self.quoteNames:
                            quote = self.quoteNames[quote]
                        feed[base][quote] = {"price": (float(result[quote.lower() + "_" + base.lower()]["last"])),
                                             "volume": (float(result[quote.lower() + "_" + base.lower()]["vol_" + base.lower()]) * self.scaleVolumeBy)}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
