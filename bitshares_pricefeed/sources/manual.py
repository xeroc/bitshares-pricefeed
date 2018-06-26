from . import FeedSource


class Manual(FeedSource):
    def _fetch(self):
        return self.feed
