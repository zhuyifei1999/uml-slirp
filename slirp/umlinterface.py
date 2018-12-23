from gevent import Greenlet
from gevent.fileobject import FileObjectThread as FileObject
import sliplib

from .ip import IPhandler


class UMLhandler(Greenlet):
    def _run(self):
        # UML communicates with us through IP over SLIP on stdin
        self.stream = FileObject(open(0, 'rb', buffering=0), bufsize=0)

        # Limitation of requiring stream to be buffered... Please duck-type
        del sliplib.SlipStream.__init__
        self.stream = sliplib.SlipStream(self.stream)

        while True:
            msg = self.stream.recv_msg()
            if not msg:
                break

            ip_version = msg[0] >> 4
            if ip_version == 4:
                from pypacker.layer3.ip import IP
                packet = IP(msg)
            elif ip_version == 6:
                from pypacker.layer3.ip6 import IP6
                packet = IP6(msg)
                # TODO: IP6 support
                continue
            else:
                # IP packet with unsupported version :(
                continue

            print(packet.bin(), file=__import__('sys').stderr, flush=True)
            IPhandler(self.stream, packet).start()
