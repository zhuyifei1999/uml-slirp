import sys

import gevent

from .umlinterface import UMLhandler


def main():
    UMLhandler().start()

    gevent.wait()


if __name__ == '__main__':
    main()
