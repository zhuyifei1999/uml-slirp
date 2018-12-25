import gevent

from .umlinterface import UMLhandler
from .daemons import die


def main():
    handler = UMLhandler()
    handler.start()
    handler.join()
    die()
    gevent.wait()


if __name__ == '__main__':
    main()
