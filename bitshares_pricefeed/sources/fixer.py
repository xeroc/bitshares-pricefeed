import csv
import json
import requests
from . import FeedSource, _request_headers


class Fixer(FeedSource):  # fixer.io daily updated data from European Central Bank.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            for base in self.bases:
                feed[base] = {}

                url = "http://api.fixer.io/latest?base=%s" % base
                response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                result = response.json()
                for quote in self.quotes:
                    if quote == base:
                        continue
                    if hasattr(self, "quoteNames") and quote in self.quoteNames:
                        quoteNew = self.quoteNames[quote]
                    else:
                        quoteNew = quote
                    feed[base][quoteNew] = {
                        "price": 1.0 / float(result["rates"][quote]),
                        "volume": 1.0}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
