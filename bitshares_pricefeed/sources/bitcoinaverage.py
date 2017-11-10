from . import FeedSource
from bitcoinaverage import RestfulClient


class BitcoinAverage(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert hasattr(self, "secret_key"), "Bitcoinaverage needs 'secret_key'"
        assert hasattr(self, "public_key"), "Bitcoinaverage needs 'public_key'"
        self.rest = RestfulClient(self.secret_key, self.public_key)

    def _fetch(self):
        feed = {}
        try:
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if quote == base:
                        continue
                    result = self.rest.ticker_global_per_symbol(
                        quote.upper() + base.upper()
                    )
                    if (
                        hasattr(self, "quoteNames") and
                        quote in self.quoteNames
                    ):
                        quote = self.quoteNames[quote]
                    feed[base][quote] = {
                        "price": (float(result["last"])),
                        "volume": (float(result["volume"]))}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
