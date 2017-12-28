import statistics
import numpy as num
import time
from pprint import pprint
from math import fabs, sqrt
from bitshares.account import Account
from bitshares.asset import Asset
from bitshares.price import Price
from bitshares.amount import Amount
from bitshares.market import Market
from concurrent import futures
from datetime import datetime, date, timedelta
from . import sources
import logging
log = logging.getLogger(__name__)

# logging.basicConfig(level=logging.INFO)


def weighted_std(values, weights):
    """ Weighted std for statistical reasons
    """
    average = num.average(values, weights=weights)
    variance = num.average((values - average) ** 2, weights=weights)  # Fast and numerically precise
    return sqrt(variance)


class Feed(object):
    feed = {}
    price = {}
    volume = {}
    price_result = {}

    def __init__(self, config):
        self.config = config
        self.reset()
        self.getProducer()

    def getProducer(self):
        """ Get the feed producers account
        """
        self.producer = Account(self.config["producer"])

    def reset(self):
        """ Reset all for-processing variables
        """
        # Do not reset feeds here!
        self.data = {}
        for base in self.config["assets"]:
            self.data[base] = {}
            for quote in self.config["assets"]:
                self.data[base][quote] = []

    def get_my_current_feed(self, asset):
        """ Obtain my own price feed for an asset
        """
        feeds = asset.feeds
        for feed in feeds:
            if feed["producer"]["id"] == self.producer["id"]:
                return feed

    def obtain_price_change(self, symbol):
        """ Store the price change to your previous feed
        """
        asset = Asset(symbol, full=True)
        price = self.price_result.get(symbol, None)
        # if not price:
        #     raise ValueError("Price for %s has not yet been derived" % symbol)
        newPrice = price["price"]
        # get my current feed
        current_feed = self.get_my_current_feed(asset)
        if current_feed and "settlement_price" in current_feed:
            oldPrice = float(current_feed["settlement_price"])
        else:
            oldPrice = float("inf")
        self.price_result[symbol]["priceChange"] = (oldPrice - newPrice) / newPrice * 100.0
        self.price_result[symbol]["current_feed"] = current_feed
        self.price_result[symbol]["global_feed"] = asset["bitasset_data"]["current_feed"]

    def obtain_flags(self, symbol):
        """ This will add attributes to price_result and indicate the results
            of a couple testsin the `flags` key
        """
        # Test flags
        self.price_result[symbol]["flags"] = []

        # Check max price change
        if fabs(self.price_result[symbol]["priceChange"]) > fabs(self.assetconf(symbol, "min_change")):
            self.price_result[symbol]["flags"].append("min_change")

        # Check max price change
        if fabs(self.price_result[symbol]["priceChange"]) > fabs(self.assetconf(symbol, "warn_change")):
            self.price_result[symbol]["flags"].append("over_warn_change")

        # Check max price change
        if fabs(self.price_result[symbol]["priceChange"]) > fabs(self.assetconf(symbol, "skip_change")):
            self.price_result[symbol]["flags"].append("skip_change")

        # Feed too old
        feed_age = self.price_result[symbol]["current_feed"]["date"] if self.price_result[symbol]["current_feed"] else datetime.min
        if (datetime.utcnow() - feed_age).total_seconds() > self.assetconf(symbol, "maxage"):
            self.price_result[symbol]["flags"].append("over_max_age")

    def get_cer(self, symbol, price):
        if (
            symbol in self.config["assets"] and
            "core_exchange_factor" in self.config["assets"][symbol]
        ):
            return price * self.assetconf(symbol, "core_exchange_factor")

        if (
            symbol in self.config["assets"] and
            "core_exchange_rate" in self.config["assets"][symbol]
        ):
            cer = self.config["assets"][symbol]["core_exchange_rate"]
            required = ["orientation", "factor", "ref_ticker"]
            if any([x not in cer for x in required]):
                raise ValueError(
                    "Missing one of required settingd for cer: {}".format(
                        str(required)))
            ticker = Market(cer["ref_ticker"]).ticker()
            price = ticker[cer["ref_ticker_attribute"]]
            price *= cer["factor"]
            orientation = Market(cer["orientation"])
            return price.as_quote(orientation["quote"]["symbol"])

    def fetch(self):
        """ Fetch the prices from external exchanges
        """
        pool = futures.ThreadPoolExecutor(max_workers=8)

        threads = {}
        if "exchanges" not in self.config or not self.config["exchanges"]:
            return

        for name, exchange in self.config["exchanges"].items():
            if "enable" in exchange and not exchange["enable"]:
                continue
            if not hasattr(sources, exchange["klass"]):
                raise ValueError("Klass %s not known!" % exchange["klass"])
            klass = getattr(sources, exchange["klass"])
            instance = klass(**exchange)
            threads[name] = pool.submit(instance.fetch)

        for name in threads:
            log.info("Checking name ...")
            self.feed[name] = threads[name].result()

    def assethasconf(self, symbol, parameter):
        """ Do we have symbol specific parameters?
        """
        if (
            symbol in self.config["assets"] and
            self.config["assets"][symbol] and
            parameter in self.config["assets"][symbol]
        ):
            return True
        return False

    def assetconf(self, symbol, parameter, no_fail=False):
        """ Obtain the configuration for an asset, if not present, use default
        """
        if (
            symbol in self.config["assets"] and
            self.config["assets"][symbol] and
            parameter in self.config["assets"][symbol]
        ):
            return self.config["assets"][symbol][parameter]
        else:
            if "default" not in self.config:
                if no_fail:
                    return
                raise ValueError("%s for %s not defined!" % (
                    parameter,
                    symbol
                ))
            if parameter not in self.config["default"]:
                if no_fail:
                    return
                raise ValueError("%s for %s not defined!" % (
                    parameter,
                    symbol
                ))

            return self.config["default"][parameter]

    def addPrice(self, base, quote, price, volume, sources=None):
        """ Add a price to the instances, temporary storage
        """
        log.info("addPrice(self, {}, {}, {}, {} (sources: {}))".format(
            base, quote, price, volume, str(sources)))
        if base not in self.data:
            self.data[base] = {}
        if quote not in self.data[base]:
            self.data[base][quote] = []

        flat_list = []
        for source in sources:
            if isinstance(source, list):
                for item in source:
                    flat_list.append(item)
            else:
                flat_list.append(source)

        self.data[base][quote].append(dict(
            price=price,
            volume=volume,
            sources=flat_list
        ))

    def appendOriginalPrices(self, symbol):
        """ Load feed data into price/volume array for processing
            This few lines solely take the data of the chosen exchanges and put
            them into price[base][quote]. Since markets are symmetric, the
            corresponding price[quote][base] is derived accordingly and the
            corresponding volume is derived at spot price
        """
        if "exchanges" not in self.config or not self.config["exchanges"]:
            return

        for datasource in self.assetconf(symbol, "sources"):
            if not self.config["exchanges"][datasource].get("enable", False):
                continue
            log.info("appendOriginalPrices({}) from {}".format(symbol, datasource))
            if datasource not in self.feed:
                continue
            for base in list(self.feed[datasource]):
                if base == "response":  # skip entries that store debug data
                    continue
                for quote in list(self.feed[datasource][base]):
                    if quote == "response":  # skip entries that store debug data
                        continue
                    if not base or not quote:
                        continue
                    # Skip markets with zero trades in the last 24h
                    if self.feed[datasource][base][quote]["volume"] == 0.0:
                        continue

                    # Original price/volume
                    self.addPrice(
                        base,
                        quote,
                        self.feed[datasource][base][quote]["price"],
                        self.feed[datasource][base][quote]["volume"],
                        sources=[datasource]
                    )

                    if self.feed[datasource][base][quote]["price"] > 0 and \
                       self.feed[datasource][base][quote]["volume"] > 0:
                        # Inverted pair price/volume
                        self.addPrice(
                            quote,
                            base,
                            float(1.0 / self.feed[datasource][base][quote]["price"]),
                            float(self.feed[datasource][base][quote]["volume"] * self.feed[datasource][base][quote]["price"]),
                            sources=[datasource]
                        )

    def derive2Markets(self, asset, target_symbol):
        """ derive BTS prices for all assets in assets_derive
            This loop adds prices going via 2 markets:
            E.g.: CNY:BTC -> BTC:BTS = CNY:BTS
            I.e.: BTS: interasset -> interasset: targetasset
        """
        symbol = asset["symbol"]

        for interasset in self.config.get("intermediate_assets", []):
            if interasset == symbol:
                continue
            for ratio in self.data[symbol][interasset]:
                if interasset in self.data and target_symbol in self.data[interasset]:
                    for idx in range(0, len(self.data[interasset][target_symbol])):
                        if self.data[interasset][target_symbol][idx]["volume"] == 0:
                            continue
                        self.addPrice(
                            symbol,
                            target_symbol,
                            float(self.data[interasset][target_symbol][idx]["price"] * ratio["price"]),
                            float(self.data[interasset][target_symbol][idx]["price"] * ratio["price"]),
                            sources=[
                                self.data[interasset][target_symbol][idx]["sources"],
                                ratio["sources"]
                            ]
                        )

    def derive3Markets(self, asset, target_symbol):
        """ derive BTS prices for all assets in assets_derive
            This loop adds prices going via 3 markets:
            E.g.: GOLD:USD -> USD:BTC -> BTC:BTS = GOLD:BTS
            I.e.: BTS: interassetA -> interassetA: interassetB -> symbol: interassetB
        """
        symbol = asset["symbol"]

        if "intermediate_assets" not in self.config or not self.config["intermediate_assets"]:
            return

        if self.assetconf(symbol, "derive_across_3markets"):
            for interassetA in self.config["intermediate_assets"]:
                for interassetB in self.config["intermediate_assets"]:
                    if interassetB == symbol:
                        continue
                    if interassetA == symbol:
                        continue
                    if interassetA == interassetB:
                        continue

                    for ratioA in self.data[interassetB][interassetA]:
                        for ratioB in self.data[symbol][interassetB]:
                            if (
                                interassetA not in self.data or
                                target_symbol not in self.data[interassetA]
                            ):
                                continue
                            for idx in range(0, len(self.data[interassetA][target_symbol])):
                                if self.data[interassetA][target_symbol][idx]["volume"] == 0:
                                    continue
                                self.addPrice(
                                    symbol,
                                    target_symbol,
                                    float(self.data[interassetA][target_symbol][idx]["price"] * ratioA["price"] * ratioB["price"]),
                                    float(self.data[interassetA][target_symbol][idx]["volume"] * ratioA["price"] * ratioB["price"]),
                                    sources=[
                                        self.data[interassetA][target_symbol][idx]["sources"],
                                        ratioA["sources"],
                                        ratioB["sources"]
                                    ]
                                )

    def type_extern(self, symbol):
        """ Derive prices when the type is 'extern' by adding data from the
            exchanges to the internal state and processing through markets
        """
        asset = Asset(symbol, full=True)
        if not asset.is_bitasset:
            return
        short_backing_asset = Asset(asset["bitasset_data"]["options"]["short_backing_asset"])
        backing_symbol = short_backing_asset["symbol"]
        asset["short_backing_asset"] = short_backing_asset

        if self.assetconf(symbol, "type") not in ["extern", "alias"]:
            return

        if self.assetconf(symbol, "type") == "alias":
            alias = self.assetconf(symbol, "alias")
            asset = Asset(alias, full=True)
        else:
            alias = symbol

        # Reset self.data
        self.reset()

        # Fill in self.data
        self.appendOriginalPrices(symbol)
        self.derive2Markets(asset, backing_symbol)
        self.derive3Markets(asset, backing_symbol)

        if alias not in self.data:
            log.warn("'{}' not in self.data".format(alias))
            return
        if backing_symbol not in self.data[alias]:
            log.warn("'backing_symbol' ({}) not in self.data[{}]".format(backing_symbol, alias))
            return
        assetvolume = [v["volume"] for v in self.data[alias][backing_symbol]]
        assetprice = [p["price"] for p in self.data[alias][backing_symbol]]

        if len(assetvolume) > 1:
            price_median = statistics.median([x["price"] for x in self.data[alias][backing_symbol]])
            price_mean = statistics.mean([x["price"] for x in self.data[alias][backing_symbol]])
            price_weighted = num.average(assetprice, weights=assetvolume)
            price_std = weighted_std(assetprice, assetvolume)
        elif len(assetvolume) == 1:
            price_median = assetprice[0]
            price_mean = assetprice[0]
            price_weighted = assetprice[0]
            price_std = 0
        else:
            print("[Warning] No market route found for %s. Skipping price" % symbol)
            return

        metric = self.assetconf(symbol, "metric")
        if metric == "median":
            p = price_median
        elif metric == "mean":
            p = price_mean
        elif metric == "weighted":
            p = price_weighted
        else:
            raise ValueError("Asset %s has an unknown metric '%s'" % (
                symbol,
                metric
            ))

        cer = self.get_cer(symbol, p)

        # price conversion to "price for one symbol" i.e.  base=*, quote=symbol
        self.price_result[symbol] = {
            "price": p,
            "cer": cer,
            "mean": price_mean,
            "median": price_median,
            "weighted": price_weighted,
            "std": price_std * 100,  # percentage
            "number": len(assetprice),
            "short_backing_symbol": backing_symbol,
            "mssr": self.assetconf(symbol, "maximum_short_squeeze_ratio"),
            "mcr": self.assetconf(symbol, "maintenance_collateral_ratio"),
            "log": self.data
        }

    def type_intern(self, symbol):
        """ Process a price from a formula
        """
        asset = Asset(symbol, full=True)
        short_backing_asset = Asset(asset["bitasset_data"]["options"]["short_backing_asset"])
        backing_symbol = short_backing_asset["symbol"]
        asset["short_backing_asset"] = short_backing_asset

        if self.assetconf(symbol, "type") != "formula":
            return

        if self.assetconf(symbol, "reference") == "extern":
            price = eval(
                self.assetconf(symbol, "formula").format(
                    **self.price_result))
        elif self.assetconf(symbol, "reference") == "intern":
            # Parse the forumla according to ref_asset
            if self.assethasconf(symbol, "ref_asset"):
                ref_asset = self.assetconf(symbol, "ref_asset")
                market = Market("%s:%s" % (ref_asset, backing_symbol))
                ticker_raw = market.ticker()
                ticker = {}
                for k, v in ticker_raw.items():
                    if isinstance(v, Price):
                        ticker[k] = float(v.as_quote("BTS"))
                    elif isinstance(v, Amount):
                        ticker[k] = float(v)
                price = eval(str(
                    self.assetconf(symbol, "formula")).format(**ticker))
            else:
                price = eval(str(self.assetconf(symbol, "formula")))
        else:
            raise ValueError("Missing 'reference' for asset %s" % symbol)

        orientation = self.assetconf(symbol, "formula_orientation", no_fail=True)\
            or "{}:{}".format(backing_symbol, symbol)   # default value
        price = Price(price, orientation)

        cer = self.get_cer(symbol, price)

        self.price_result[symbol] = {
            "price": float(price.as_quote(backing_symbol)),
            "cer": cer,
            "number": 1,
            "short_backing_symbol": backing_symbol,
            "mean": price,
            "median": price,
            "weighted": price,
            "mssr": self.assetconf(symbol, "maximum_short_squeeze_ratio"),
            "mcr": self.assetconf(symbol, "maintenance_collateral_ratio"),
            "std": 0.0,
            "number": 1,
        }

    def derive(self, assets_derive=set()):
        """ calculate self.feed prices in BTS for all assets given the exchange prices in USD,CNY,BTC,...
        """
        # Manage default assets to publish
        assets_derive = set(assets_derive)
        if not assets_derive:
            assets_derive = set(self.config["assets"])

        # create returning dictionary
        self.price_result = {}
        for symbol in assets_derive:
            self.price_result[symbol] = {}

        # Derive 'external' price feed
        for symbol in assets_derive:
            self.type_extern(symbol)

        # Formula feeds
        for symbol in assets_derive:
            self.type_intern(symbol)

        # tests
        for symbol in assets_derive:
            if not self.price_result.get(symbol):
                continue
            self.obtain_price_change(symbol)
            self.obtain_flags(symbol)

        return self.price_result

    def get_prices(self):
        return self.price_result
