import requests
from . import FeedSource, _request_headers


class Lbank(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            url = "https://api.lbank.info/v1/ticker.do?symbol={quote}_{base}"
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if quote == base:
                        continue
                    response = requests.get(
                        url=url.format(
                            base=base.lower(),
                            quote=quote.lower()
                        ),
                        headers=_request_headers, timeout=self.timeout)
                    result = response.json()["ticker"]
                    if hasattr(self, "quoteNames") and quote in self.quoteNames:
                        quote = self.quoteNames[quote]
                    feed[base][quote] = {
                        "price": (float(result["latest"])),
                        "volume": (float(result["vol"]) * self.scaleVolumeBy)}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
