import pytest
import os
import yaml
import math

@pytest.fixture
def conf(request):
    confName = getattr(request.module, 'config')
    basePath = os.path.join(os.path.dirname(__file__), '../../')
    confDir = os.path.join(basePath, confName)
    conf = yaml.load(open(confDir))
    producer = getattr(request.module, 'producer', 'null-account')
    conf['producer'] = producer
    return conf

class Checkers:
    @staticmethod
    def check_price(prices, computedAssetName, collateralName, maxSpread):
        print(prices)
        assert computedAssetName in prices   
        assetPrice = prices[computedAssetName]
        for field in ['mean', 'global_feed', 'price', 'weighted', 'cer', 
                      'priceChange', 'mssr', 'current_feed', 'short_backing_symbol', 
                      'median', 'mcr', 'std', 'number']:
            assert field in assetPrice
        assert collateralName == assetPrice['short_backing_symbol']
        feedPrice = assetPrice['global_feed']['settlement_price'].as_quote(collateralName)['price']
        computedPrice = assetPrice['price']
        assert  math.fabs(1 - (computedPrice / feedPrice)) < maxSpread

@pytest.fixture
def checkers():
    return Checkers

