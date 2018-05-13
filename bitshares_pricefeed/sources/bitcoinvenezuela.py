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
            # FIXME: SSL check deactivated, issue with Comodo SSL certificate.
            url = "https://api.bitcoinvenezuela.com"
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout, verify=False)
            result = response.json()
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if quote in result and base in result[quote]:
                        feed[base][quote] = {"price": result[quote][base],
                                            "volume": 1.0}
                    else:
                        exchange_rate = base + '_' + quote
                        if exchange_rate in result["exchange_rates"]:
                            feed[base][quote] = {"price": result["exchange_rates"][exchange_rate],
                                                "volume": 1.0}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
