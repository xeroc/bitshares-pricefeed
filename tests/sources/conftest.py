import pytest

class Checkers:
    @staticmethod
    def check_feed(feed, pairs, **kargs):
        print(feed)
        for pair in pairs:
            (quote, base) = pair.split(':')
            assert base in feed
            assert quote in feed[base]
            for f in ['volume', 'price']:
                assert f in feed[base][quote]
                assert feed[base][quote][f] > 0.0
            if 'noVolume' in kargs and kargs['noVolume']:
                assert feed[base][quote]['volume'] == 1.0

@pytest.fixture
def checkers():
    return Checkers

