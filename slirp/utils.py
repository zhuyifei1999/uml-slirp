import random


class RandomIntSequential:
    __slots__ = ('_cur', '_max')

    def __init__(self, bits):
        self._max = 1 << bits
        self._cur = random.randrange(self._max // 2)

    def __str__(self):
        return '<RandomIntSequential with maxsize={} and current={}'.format(
            self._max, self._cur
        )

    def __add__(self, other):
        self._cur += other
        self._cur %= self._max

    def __int__(self):
        return self._cur
