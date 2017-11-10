import csv
import json
import requests
from . import FeedSource, _request_headers


class Bittrex(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            url = "https://bittrex.com/api/v1.1/public/getmarketsummaries"
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()["result"]
            feed["response"] = response.json()
            for base in self.bases:
                feed[base] = {}
                for thisMarket in result:
                    for quote in self.quotes:
                        if quote == base:
                            continue
                        if thisMarket["MarketName"] == base + "-" + quote:
                            if hasattr(self, "quoteNames") and quote in self.quoteNames:
                                quote = self.quoteNames[quote]
                            feed[base][quote] = {"price": (float(thisMarket["Last"])),
                                                 "volume": (float(thisMarket["Volume"]) * self.scaleVolumeBy)}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
