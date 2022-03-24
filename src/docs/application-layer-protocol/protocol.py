'''
Date: 2021.11.13 17:27
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2021.11.13 17:27
'''
import socket
import struct
from datetime import datetime
from enum import IntEnum
from functools import reduce
from operator import xor
from typing import NamedTuple, Tuple


class State(IntEnum):
    START = 1
    STOP = 2
    ESCAPE = 3
    CONTINUE = 4


class Symbol(IntEnum):
    START = 0x7e
    STOP = 0x7e
    ESCAPE = 0x7d


class ClientMethod(IntEnum):
    REGISTER = 0x0100
    AUTHENTICATION = 0x0102
    LOCATION_REPORT = 0x0200
    HEARTBEAT = 0x0002


class ServerMethod(IntEnum):
    REGISTER = 0x8100
    COMMON = 0x8001
    LOCATION_QUERY = 0x8201


class Header(NamedTuple):
    METHOD: int
    LENGTH: int
    IMEI: str
    NUMBER: int

    def marshal(self) -> bytes:
        return struct.pack('>2H6BH', self.METHOD, self.LENGTH,
                           *bytes.fromhex(self.IMEI), self.NUMBER)

    @staticmethod
    def unmarshal(header: bytes) -> 'Header':
        obj = struct.unpack('>2H6BH', header)
        return Header(obj[0], obj[1], bytearray(obj[2:8]).hex(), obj[8])


class Location(NamedTuple):
    ALARM_SIGN: int
    STATE: int
    LATITUDE: float
    LONGITUDE: float
    ALTITUDE: int
    SPEED: int
    DIRECTION: int
    DATETIME: datetime

    @staticmethod
    def unmarshal(location: bytes) -> 'Location':
        obj = struct.unpack('>4L3H6B', location)
        return Location(obj[0], obj[1], obj[2] / 1000000, obj[3] / 1000000, obj[4], obj[5], obj[6],
                        datetime.strptime(bytearray(obj[7:]).hex(), '%y%m%d%H%M%S'))


class Parser(object):
    _escape = (
        (bytearray([0x7d]), bytearray([0x7d, 0x01])),
        (bytearray([0x7e]), bytearray([0x7d, 0x02])),
    )

    def __init__(self, client: socket.socket):
        self._client = client
        self._packet = bytearray()
        self._state = State.STOP
        self._table = {
            State.START: [State.START, State.STOP, State.ESCAPE, State.CONTINUE],
            State.STOP: [State.START, State.STOP, State.STOP, State.STOP],
            State.ESCAPE: [State.CONTINUE, State.CONTINUE, State.CONTINUE, State.CONTINUE],
            State.CONTINUE: [State.START, State.STOP, State.ESCAPE, State.CONTINUE],
        }

    def _get_index(self, symbol):
        if Symbol.START != Symbol.STOP:
            return {
                Symbol.START: 0,
                Symbol.STOP: 1,
                Symbol.ESCAPE: 2,
            }.get(symbol, 3)

        if self._state != State.STOP:
            return {
                Symbol.STOP: 1,
                Symbol.ESCAPE: 2,
            }.get(symbol, 3)

        if self._state != State.START:
            return {
                Symbol.START: 0,
                Symbol.ESCAPE: 2,
            }.get(symbol, 3)

    def _put(self, symbol: int):
        self._state = self._table[self._state][self._get_index(symbol)]

        if self._state == State.START:
            self._packet.clear()
        elif self._state == State.STOP:
            if self._packet:
                header, response, body = self.parse(self._packet)

                if header.METHOD == ClientMethod.LOCATION_REPORT:
                    body = Location.unmarshal(body[:28])
                    print(body)

                if response:
                    self._client.sendall(self.combine(response))

                self._packet.clear()
        elif self._state >= State.ESCAPE:
            self._packet.append(symbol)

    def put(self, symbols: bytes):
        for symbol in symbols:
            self._put(symbol)

    @staticmethod
    def parse(packet: bytearray) -> Tuple[Header, bytes, bytearray]:
        # 逆转义
        for key, value in Parser._escape:
            packet = packet.replace(value, key)

        if len(packet) < 12:
            return Header(0, 0, '', 0), b'', bytearray()

        header = Header.unmarshal(packet[0:12])
        body = packet[12:]

        if header.METHOD == ClientMethod.REGISTER:
            response_body = struct.pack('>HBL', header.NUMBER, 0, 20211115)
            response = Header(ServerMethod.REGISTER, len(response_body),
                              header.IMEI, header.NUMBER).marshal() + response_body
        else:
            response_body = struct.pack('>2HB', header.NUMBER, header.METHOD, 0)
            response = Header(ServerMethod.COMMON, len(response_body),
                              header.IMEI, header.NUMBER).marshal() + response_body

        return header, response, body

    @staticmethod
    def combine(body: bytes) -> bytes:
        body = bytearray([*body, reduce(xor, body)])

        # 转义
        for key, value in Parser._escape:
            body = body.replace(key, value)

        return bytearray([Symbol.START, *body, Symbol.STOP]).hex().encode('ascii')
