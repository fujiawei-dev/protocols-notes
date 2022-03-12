"""
Date: 2022.03.11 18:00
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2022.03.11 18:00
"""
import base64
import socket
from threading import Lock
from typing import Union
from random import randbytes

from common import WebSocketProtocol, log, parse_http_headers

log = log.getChild("client")

websocket_upgrade_template_client = (
    "GET / TTP/1.1\r\n"
    "Sec-WebSocket-Version: 13\r\n"
    "Sec-WebSocket-Key: {0}\r\n"
    "Connection: Upgrade\r\n"
    "Upgrade: websocket\r\n"
    "Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits\r\n"
    "Host: {1}\r\n\r\n"
)


class WebSocketClient(WebSocketProtocol):
    """WebSocket Protocol Implementation for Client."""

    client: socket.socket = None
    client_address: str = ""

    lock = Lock()
    closed = False

    def __init__(self, host: str = "localhost", port: Union[str, int] = 8089):
        self._host, self._port = host, port
        self.connect(host, port)

    def __str__(self):
        return "<client:%s, remote_address:%s>" % (self.address, self.remote_address)

    def connect(self, host: str = "localhost", port: Union[str, int] = 8089):
        self._host, self._port = host or self._host, port or self._port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self._host, self._port))
        self.client_address = self.client.getsockname()
        self.handshake()

    @property
    def address(self):
        return f"%s:%d" % self.client_address

    @property
    def remote_address(self):
        return f"{self._host}:{self._port}"

    def close(self):
        log.info(f"close {self}")

        if not self.closed:
            with self.lock:
                self.closed = True
                self.client.close()

        log.info(f"{self} closed")

    def serve(self):
        if not self.handshake():
            log.error(f"{self} handshake failed")
            self.close()
            return

        log.info(f"{self} handshake succeeded")

        self.client.settimeout(5)

        while True:
            with self.lock:
                if self.closed:
                    break

                try:
                    try:
                        data = self.client.recv(self.buffer_size)
                    except socket.timeout:
                        continue
                except KeyboardInterrupt:
                    break

            if data:
                log.info(f"{self} recv {data!r}")
                frame = self.unpack_data_to_frame(data)

    def handshake(self) -> bool:
        self._send(
            websocket_upgrade_template_client.format(
                base64.b64encode(randbytes(16)).decode("utf-8"),
                self.remote_address,
            ).encode("utf-8")
        )

        self.client.settimeout(3)
        data = self.client.recv(self.buffer_size)
        log.info(f"{self} recv {data!r}")

        headers = parse_http_headers(data.decode("utf-8"), from_request=False)

        return True

    def _send(self, data):
        log.info(f"{self} will send {data!r}")
        self.client.send(data)

    def send_message(self, message):
        pass
