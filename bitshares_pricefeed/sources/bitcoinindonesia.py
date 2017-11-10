import csv
import json
import requests
from . import FeedSource, _request_headers


class BitcoinIndonesia(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if quote == base:
                        continue
                    url = "https://vip.bitcoin.co.id/api/%s_%s/ticker" % (quote.lower(), base.lower())
                    response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                    result = response.json()["ticker"]
                    if hasattr(self, "quoteNames") and quote in self.quoteNames:
                        quote = self.quoteNames[quote]
                    feed[base][quote] = {"price": float(result["last"]),
                                         "volume": float(result["vol_" + quote.lower()]) * self.scaleVolumeBy}
                    feed[base]["response"] = response.json()
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
