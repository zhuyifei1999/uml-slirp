import random

from gevent.lock import RLock


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


class FragmentReassembler:
    __slots__ = ('_data', '_ready', '_sizefreeze', '_lock')

    class FragmentOverlap(ValueError):
        pass

    class ExtendPastLast(ValueError):
        pass

    class NotReady(Exception):
        pass

    def __init__(self):
        self._data = bytearray()
        self._ready = bytearray()
        self._sizefreeze = False
        self._lock = RLock()

    def bin(self):
        if not self._sizefreeze or not all(self._ready):
            raise self.NotReady

        return bytes(self._data)

    def _ensure_size(self, end):
        cursize = len(self._data)
        if end <= cursize:
            return

        if self._sizefreeze:
            raise self.ExtendPastLast

        addsize = end - cursize
        self._data.extend(0 for i in range(addsize))
        self._ready.extend(0 for i in range(addsize))

        assert len(self._data) == len(self._ready)

    def extend(self, data, offset, last):
        with self._lock:
            end = offset + len(data)
            self._ensure_size(end)

            if any(self._ready[offset:end]):
                raise self.FragmentOverlap

            if last:
                if self._sizefreeze:
                    raise self.ExtendPastLast
                self._sizefreeze = True

            self._data[offset:end] = data
            self._ready[offset:end] = (1 for i in range(len(data)))
