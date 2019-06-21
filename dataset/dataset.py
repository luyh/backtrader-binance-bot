import backtrader as bt
import itertools
import datetime
class CustomDataset(bt.feeds.GenericCSVData):
    params = (
        ('time', -1),
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('openinterest', 6),
    )

class OneTokenDataset(bt.feeds.GenericCSVData):
    params = (
        ('time', -1),
        ('datetime', 4),
        ('open', 3),
        ('high', 1),
        ('low', 2),
        ('close', 0),
        ('volume', 5),
        ('openinterest', -1),
    )

