import datetime
import requests
from . import FeedSource, _request_headers
import quandl


class Quandl(FeedSource):  # Google Finance
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = 60 * 60  # 1h
        self.days = 1
        self.maxAge = getattr(self, "maxAge", 5)

        quandl.ApiConfig.api_key = self.api_key
        quandl.ApiConfig.api_version = '2015-04-09'

    def _fetch(self):
        feed = {}

        try:
            for market in self.datasets:
                quote, base = market.split(":")
                if base not in feed:
                    feed[base] = {}

                prices = []
                for dataset in self.datasets[market]:
                    data = quandl.get(dataset, rows=1, returns='numpy')
                feed[base][quote] = {"price": data[0][1],
                                     "volume": 1.0}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed


class QuandlPlain(FeedSource):  # Google Finance
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = 60 * 60  # 1h
        self.days = 1
        self.maxAge = getattr(self, "maxAge", 5)

    def _fetch(self):
        feed = {}

        try:
            for market in self.datasets:
                quote, base = market.split(":")
                if base not in feed:
                    feed[base] = {}

                prices = []
                for dataset in self.datasets[market]:
                    url = "https://www.quandl.com/api/v3/datasets/{dataset}.json?start_date={date}".format(
                        dataset=dataset,
                        date=datetime.datetime.strftime(datetime.datetime.now() -
                                                        datetime.timedelta(days=self.maxAge),
                                                        "%Y-%m-%d")
                    )
                    response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                    data = response.json()
                    if "quandl_error" in data:
                        raise Exception(data["quandl_error"]["message"])
                    if "dataset" not in data:
                        raise Exception("Feed has not returned a dataset for url: %s" % url)
                    d = data["dataset"]
                    if len(d["data"]):
                        prices.append(d["data"][-1][1])

                feed[base][quote] = {"price": sum(prices) / len(prices),
                                     "volume": 1.0}
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
