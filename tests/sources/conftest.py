import pytest

class Checkers:
    @staticmethod
    def check_feed(feed, quotes, bases):
        print(feed)
        for base in bases:
            assert base in feed
            for quote in quotes:
                assert quote in feed[base]
                for f in ['volume', 'price']:
                    assert f in feed[base][quote]

@pytest.fixture
def checkers():
    return Checkers

