"""
Date: 2022.03.12 08:02
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2022.03.12 08:02
"""
import logging
from enum import IntEnum
from io import StringIO
from random import randbytes
from dataclasses import dataclass

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s %(message)s",
)

log = logging.getLogger("websocket")


def parse_http_headers(content: str, from_request=True) -> dict:
    fp = StringIO(content)
    headers = {}

    if from_request:
        method, path, http_version = fp.readline().split()
        headers = {"Method": method, "Path": path, "HTTP-Version": http_version}

    for line in fp.readlines():
        if line.find(": ") != -1:
            k, v = line.split(": ")
            headers[k.strip()] = v.strip()

    return headers


class WebSocketOpcode(IntEnum):
    """Indicates the type of frame"""

    ContinuationFrame = 0
    TextFrame = 1
    BinaryFrame = 2
    ConnectionCloseFrame = 8
    PingFrame = 9
    PongFrame = 10


@dataclass()
class WebSocketFrame(object):
    """Represents a WebSocket data frame"""

    FIN: int = 1  # 1 bit
    Opcode: int = 0  # 4 bit
    MASK: int = 1  # 1 bit
    PayloadLength: int = 0  # 7 bit

    ExtendedPayloadLength: int = 0  # 16 bit
    MaskingKey: bytes = b""  # 16 bit
    PayloadData: bytes = b""

    def __str__(self):
        return (
            "<class WebSocketFrame:"
            f"FIN={self.FIN}, "
            f"Opcode={self.Opcode}, "
            f"MASK={self.MASK}, "
            f"PayloadLength={self.PayloadLength}, "
            f"ExtendedPayloadLength={self.ExtendedPayloadLength}, "
            f"MaskingKey={self.MaskingKey!r}, "
            f"PayloadData={self.PayloadData!r}"
            ">"
        )


class WebSocketProtocol(object):
    """WebSocket Common Protocol"""

    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    buffer_size: int = 1024

    @staticmethod
    def unpack_data_to_frame(data: bytes) -> WebSocketFrame:
        frame = WebSocketFrame()

        frame.FIN = data[0] >> 7
        frame.Opcode = data[0] & 15
        frame.MASK = data[1] >> 7
        frame.PayloadLength = data[1] & 127

        if frame.PayloadLength == 126:
            frame.ExtendedPayloadLength = data[2:4]
            frame.MaskingKey = data[4:8]
            frame.PayloadData = data[8:]
        elif frame.PayloadLength == 127:
            frame.ExtendedPayloadLength = data[2:10]
            frame.MaskingKey = data[10:14]
            frame.PayloadData = data[14:]
        else:
            frame.ExtendedPayloadLength = 0
            frame.MaskingKey = data[2:6]
            frame.PayloadData = data[6:]

        if frame.MASK:
            payload_data = bytearray()
            for i in range(len(frame.PayloadData)):
                chunk = frame.PayloadData[i] ^ frame.MaskingKey[i % 4]
                payload_data.append(chunk)
            frame.PayloadData = payload_data

        log.debug(frame)
        # log.debug(WebSocketProtocol.pack_frame_to_data(frame))

        return frame

    @staticmethod
    def pack_frame_to_data(frame: WebSocketFrame) -> bytes:
        data = bytearray()
        data.append(frame.FIN << 7 | frame.Opcode)
        data.append(frame.MASK << 7 | frame.PayloadLength)

        if not frame.MaskingKey:
            frame.MaskingKey = randbytes(4)

        data.extend(bytearray(frame.MaskingKey))

        payload_data = bytearray()
        for i in range(len(frame.PayloadData)):
            chunk = frame.PayloadData[i] ^ frame.MaskingKey[i % 4]
            payload_data.append(chunk)

        data.extend(bytearray(payload_data))

        return bytes(data)

    def handle_frame(self, frame: WebSocketFrame):
        if frame.Opcode == WebSocketOpcode.ConnectionCloseFrame:
            self.close()
        elif frame.Opcode == WebSocketOpcode.PingFrame:
            self.pong()
        else:
            return frame.PayloadData

    def ping(self):
        self._send(
            self.pack_frame_to_data(WebSocketFrame(Opcode=WebSocketOpcode.PingFrame))
        )

    def pong(self):
        self._send(
            self.pack_frame_to_data(WebSocketFrame(Opcode=WebSocketOpcode.PongFrame))
        )

    def _send(self, data):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
