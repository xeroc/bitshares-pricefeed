import json
import requests
from . import FeedSource, _request_headers


class Coindesk(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            url = "https://api.coindesk.com/v1/bpi/currentprice/{base}.json"
            for base in self.bases:
                feed[base] = {}
                for quote in self.quotes:
                    if quote != 'BTC':
                        raise Exception('Coindesk FeedSource only handle BTC quotes.')
                    response = requests.get(url=url.format(
                        base=base
                    ), headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                    feed[base][quote] = { 
                        "price": float(result['bpi'][base]['rate_float']),
                        "volume": 1.0
                    }
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed