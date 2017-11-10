import csv
import json
import requests
from . import FeedSource, _request_headers


class CurrencyLayer(FeedSource):  # Hourly updated data over http with free subscription
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, "api_key") or not hasattr(self, "free_subscription"):
            raise Exception("CurrencyLayer FeedSource requires 'api_key' and 'free_subscription'")

    def _fetch(self):
        feed = {}
        try:
            for base in self.bases:
                url = "http://apilayer.net/api/live?access_key=%s&currencies=%s&source=%s&format=1" % (self.api_key, ",".join(self.quotes), base)
                if self.free_subscription:
                    if base == 'USD':
                        response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                        result = response.json()
                    else:
                        continue
                else:
                    response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                if result["source"] == base:
                    feed[base] = {}
                    for quote in self.quotes:
                        if quote == base:
                            continue
                        if hasattr(self, "quoteNames") and quote in self.quoteNames:
                            quoteNew = self.quoteNames[quote]
                        else:
                            quoteNew = quote
                        feed[base][quoteNew] = {
                            "price": result["quotes"][base + quote],
                            "volume": 1.0}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
