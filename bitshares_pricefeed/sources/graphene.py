import csv
import json
import requests
from . import FeedSource, _request_headers


class Graphene(FeedSource):
    def _fetch(self):
        from bitshares.market import Market
        feed = {}
        try:
            for base in self.bases:
                for quote in self.quotes:
                    if quote == base:
                        continue
                    ticker = Market("%s:%s" % (quote, base)).ticker()
                    if hasattr(self, "quoteNames") and quote in self.quoteNames:
                        quote = self.quoteNames[quote]
                    feed[base] = {}
                    if (float(ticker["latest"])) > 0 and float(ticker["quoteVolume"]) > 0:
                        feed[base][quote] = {"price": (float(ticker["latest"])),
                                             "volume": (float(ticker["quoteVolume"]) * self.scaleVolumeBy)}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
