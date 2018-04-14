import csv
import json
import requests
from . import FeedSource, _request_headers


class Binance(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            url = "https://www.binance.com/api/v1/ticker/24hr?symbol={quote}{base}"
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if quote == base:
                        continue
                    # btcusd, btceur
                    response = requests.get(url=url.format(
                        quote=quote,
                        base=base
                    ), headers=_request_headers, timeout=self.timeout)
                    result = response.json()

         #           if hasattr(self, "quoteNames") and quote in self.quoteNames:
         #              quote = self.quoteNames[quote]
                    feed[base][quote] = {"price": (float(result["lastPrice"])),
                                         "volume": (float(result["volume"])* self.scaleVolumeBy)}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed

