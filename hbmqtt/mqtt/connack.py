# Copyright (c) 2015 Nicolas JOUANIN
#
# See the file license.txt for copying permission.
import asyncio
from hbmqtt.mqtt.packet import CONNACK, MQTTPacket, MQTTFixedHeader, MQTTVariableHeader
from hbmqtt.codecs import int_to_bytes, read_or_raise, bytes_to_int
from hbmqtt.errors import HBMQTTException
from hbmqtt.adapters import ReaderAdapter

CONNECTION_ACCEPTED = 0x00
UNACCEPTABLE_PROTOCOL_VERSION = 0x01
IDENTIFIER_REJECTED = 0x02
SERVER_UNAVAILABLE = 0x03
BAD_USERNAME_PASSWORD = 0x04
NOT_AUTHORIZED = 0x05


class ConnackVariableHeader(MQTTVariableHeader):
    def __init__(self, session_parent=None, return_code=None):
        super().__init__()
        self.session_parent = session_parent
        self.return_code = return_code

    @classmethod
    def from_stream(cls, reader: ReaderAdapter, fixed_header: MQTTFixedHeader):
        data = yield from read_or_raise(reader, 2)
        session_parent = data[0] & 0x01
        return_code = bytes_to_int(data[1])
        return cls(session_parent, return_code)

    def to_bytes(self):
        out = bytearray(2)
        # Connect acknowledge flags
        if self.session_parent:
            out[0] = b'\x01'
        else:
            out[0] = b'\x00'
        # return code
        out[1] = int_to_bytes(self.return_code)

        return out

    def __repr__(self):
        return type(self).__name__ + '(session_parent={0}, return_code={1})'\
            .format(hex(self.session_parent), hex(self.return_code))


class ConnackPacket(MQTTPacket):
    VARIABLE_HEADER = ConnackVariableHeader
    PAYLOAD = None

    def __init__(self, fixed: MQTTFixedHeader=None, variable_header: ConnackVariableHeader=None, payload=None):
        if fixed is None:
            header = MQTTFixedHeader(CONNACK, 0x00)
        else:
            if fixed.packet_type is not CONNACK:
                raise HBMQTTException("Invalid fixed packet type %s for ConnackPacket init" % fixed.packet_type)
            header = fixed
        super().__init__(header)
        self.variable_header = variable_header
        self.payload = None

    @classmethod
    def build(cls, session_parent=None, return_code=None):
        v_header = ConnackVariableHeader(session_parent, return_code)
        packet = ConnackPacket(variable_header=v_header)
        return packet
