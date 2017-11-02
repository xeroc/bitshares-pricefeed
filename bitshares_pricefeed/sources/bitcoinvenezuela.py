import csv
import json
import requests
from . import FeedSource, _request_headers


class BitcoinVenezuela(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            url = "http://api.bitcoinvenezuela.com"
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()
            for base in self.bases:
                feed[base] = {}
                if base == "USD":
                    for quote in self.quotes:
                        if quote == base or quote and quote not in ["EUR", "VEF", "ARS"]:
                            continue
                        feed[base][quote] = {"price": result["exchange_rates"][quote + '_' + base],
                                             "volume": 1.0}
                    continue
                for quote in self.quotes:
                    if quote == base:
                        continue
                    feed[base][quote] = {"price": result[base][quote],
                                         "volume": 1.0}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
