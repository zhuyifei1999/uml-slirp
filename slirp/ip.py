import weakref

from gevent import Greenlet
from pypacker.layer3.ip import IP

from .constants import MTU
from .utils import RandomIntSequential

sendids = weakref.WeakKeyDictionary()


class IPhandler(Greenlet):
    # TODO: IP6 support

    def __init__(self, stream, packet):
        super().__init__()
        self.stream = stream
        self.packet = packet

    def respond(self, protocol, payload):
        if self.stream not in sendids:
            sendids[self.stream] = RandomIntSequential(16)
        sendid = sendids[self.stream]
        sendid += 1

        response = IP(id=int(sendid), p=protocol,
                      src=self.packet.dest, dst=self.packet.src)

        if len(response.bin()) > (MTU & ~0b111):
            response = response.create_fragments()
        else:
            response = [response]

        for packet in response:
            self.stream.send_msg(packet.bin())

    def _run(self):
        print(self.packet, file=__import__('sys').stderr, flush=True)
        pass
