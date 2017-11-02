import re
import csv
import json
import requests
from . import FeedSource, _request_headers


class ChBTC(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        url = "http://api.chbtc.com/data/v1/ticker?currency={quote}_{base}"  # bts_cny
        try:
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if base == quote:
                        continue
                    response = requests.get(url=url.format(
                        quote=quote,
                        base=base
                    ), headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                    feed["response"] = result
                    if "ticker" in result and \
                       "last" in result["ticker"] and \
                       "vol" in result["ticker"]:
                        if hasattr(self, "quoteNames") and quote in self.quoteNames:
                            quote = self.quoteNames[quote]
                        feed[base][quote] = {"price": (float(result["ticker"]["last"])),
                                             "volume": (float(result["ticker"]["vol"]) * self.scaleVolumeBy)}
                    else:
                        print("\nFetched data from {0} is empty!".format(type(self).__name__))
                        continue
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
