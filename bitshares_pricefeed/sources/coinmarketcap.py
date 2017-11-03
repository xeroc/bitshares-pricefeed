import csv
import json
import requests
from . import FeedSource, _request_headers


class Coinmarketcap(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            url = 'https://api.coinmarketcap.com/v1/ticker/'
            response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()
            base = self.bases[0]
            if base == 'BTC':
                feed[base] = {}
                for quote in self.quotes:
                    if quote == base:
                        continue
                    for r in result:
                        if r["symbol"] == base.upper():
                            feed["BTC"][quote] = {
                                "price": (float(result["price_btc"])),
                                "volume": (float(result["24h_volume_usd"]) / float(result["price_btc"]) * self.scaleVolumeBy)}
                            feed["USD"][quote] = {
                                "price": (float(result["price_usd"])),
                                "volume": (float(result["24h_volume_usd"]) * self.scaleVolumeBy)}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        self._fetch_altcap()

        return feed

    def _fetch_altcap(self):
        feed = {}
        base = self.bases[0]
        if base == 'BTC':
            feed[base] = {}
            try:
                ticker = requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
                global_data = requests.get('https://api.coinmarketcap.com/v1/global/').json()
                bitcoin_data = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/').json()[0]
                alt_caps_x = [float(coin['market_cap_usd'])
                              for coin in ticker if
                              float(coin['rank']) <= 11 and
                              coin['symbol'] != "BTC"
                              ]
                alt_cap = (
                    float(global_data['total_market_cap_usd']) -
                    float(bitcoin_data['market_cap_usd']))
                alt_cap_x = sum(alt_caps_x)
                btc_cap = next((coin['market_cap_usd'] for coin in ticker if coin["symbol"] == "BTC"))

                btc_altcap_price = float(alt_cap) / float(btc_cap)
                btc_altcapx_price = float(alt_cap_x) / float(btc_cap)

                if 'ALTCAP' in self.quotes:
                    feed[base]['ALTCAP'] = {"price": btc_altcap_price,
                                            "volume": 1.0}
                if 'ALTCAP.X' in self.quotes:
                    feed[base]['ALTCAP.X'] = {"price": btc_altcapx_price,
                                              "volume": 1.0}
            except Exception as e:
                raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
