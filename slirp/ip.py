import weakref

from expiringdict import ExpiringDict
from gevent import Greenlet
from pypacker.layer3.ip import IP

from .constants import MTU
from .daemons import handle_expiringdict
from .utils import RandomIntSequential, FragmentReassembler

sendids = weakref.WeakKeyDictionary()
fragments = weakref.WeakKeyDictionary()


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
        if self.stream not in fragments:
            fragments[self.stream] = ExpiringDict(max_len=16,
                                                  max_age_seconds=300)
            handle_expiringdict(fragments[self.stream])

        packetid = self.packet.id

        if packetid not in fragments[self.stream]:
            # I'd love to use a tuple here, but it's not mutable :(
            fragments[self.stream][packetid] = [
                None, FragmentReassembler()]

        fragments[self.stream][packetid][1].extend(
            self.packet.body_bytes,
            self.packet.offset * 8,
            not self.packet.flags & 0b1
        )

        if not self.packet.offset:
            fragments[self.stream][packetid][0] = self.packet

        try:
            body = fragments[self.stream][packetid][1].bin()
        except FragmentReassembler.NotReady:
            return

        self.packet = fragments[self.stream][packetid][0]
        self.packet.body_bytes = body

        del fragments[self.stream][packetid]

        print(self.packet, file=__import__('sys').stderr, flush=True)
