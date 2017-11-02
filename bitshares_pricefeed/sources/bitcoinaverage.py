import csv
import json
import requests
from . import FeedSource, _request_headers

from bitcoinaverage import RestfulClient


class BitcoinAverage(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rest = RestfulClient(self.secret_key, self.public_key)

    def _fetch(self):
        feed = {}
        try:
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if quote == base:
                        continue
                    response = self.rest.ticker_all_global(crypto='BTC', fiat='USD,EUR')
                    print(response)
                    response = requests.get(url=url.format(
                        quote=quote,
                        base=base
                    ), headers=_request_headers, timeout=self.timeout)
                    print(response.text)
                    result = response.json()
                    if hasattr(self, "quoteNames") and quote in self.quoteNames:
                        quote = self.quoteNames[quote]
                    feed[base]["response"] = result
                    feed[base][quote] = {"price": (float(result["last"])),
                                         "volume": (float(result["total_vol"]))}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
