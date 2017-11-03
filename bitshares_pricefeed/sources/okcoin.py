import sys
import csv
import json
import requests
from . import FeedSource, _request_headers


class Okcoin(FeedSource):
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
                    if base == "USD":
                        url = "https://www.okcoin.com/api/v1/ticker.do?symbol=%s_%s" % (quote.lower(), base.lower())
                    elif base == "CNY":
                        url = "https://www.okcoin.cn/api/ticker.do?symbol=%s_%s" % (quote.lower(), base.lower())
                    else:
                        sys.exit("\n%s does not know base type %s" % (type(self).__name__, base))
                    response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                    if hasattr(self, "quoteNames") and quote in self.quoteNames:
                        quote = self.quoteNames[quote]
                    feed[base]["response"] = result
                    feed[base][quote] = {"price": (float(result["ticker"]["last"])),
                                         "volume": (float(result["ticker"]["vol"]) * self.scaleVolumeBy)}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
