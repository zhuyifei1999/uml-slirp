import weakref

from gevent import Greenlet, idle, sleep, killall

daemons = set()


class Daemon(Greenlet):
    def __init__(self, wait=1):
        super().__init__()
        self.wait = wait

    def _run(self):
        daemons.add(self)
        while True:
            # FiXME: need a better way of saying 'block until something else
            # is scheduled and finished running, and is idle'. Something like
            # Services.tm.currentThread.processNextEvent(true);
            # in XUL
            sleep(self.wait)
            idle()
            self.scheduled()

    def scheduled(self):
        raise NotImplementedError


def die():
    daemons_copy = set(daemons)
    daemons.clear()
    killall(daemons_copy)


# Specific daemons

class ExpireDict(Daemon):
    def __init__(self):
        super().__init__()
        # I'd love to use WeakSet here, but dicts aren't hashable :(
        self.dicts = []

    def scheduled(self):
        for dctref in list(self.dicts):
            dct = dctref()
            if dct is None:
                self.dicts.remove(dctref)
                continue

            for key, value in dct.items():
                pass


def handle_expiringdict(dct):
    expire_dict_thread = filter(lambda t: isinstance(t, ExpireDict), daemons)
    expire_dict_thread = list(expire_dict_thread)

    if not expire_dict_thread:
        expire_dict_thread = ExpireDict()
        expire_dict_thread.start()
    else:
        expire_dict_thread = expire_dict_thread[0]

    # expire_dict_thread.dicts.add(dct)
    expire_dict_thread.dicts.append(weakref.ref(dct))
