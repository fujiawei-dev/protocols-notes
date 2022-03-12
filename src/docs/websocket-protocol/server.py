"""
Date: 2022.03.11 19:04
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2022.03.11 19:04
"""
import base64
import hashlib
import socket
from threading import Thread, Lock
from typing import Union
from common import log, WebSocketProtocol, parse_http_headers

log = log.getChild("server")


websocket_upgrade_template_server = (
    "HTTP/1.1 101 Switching Protocols\r\n"
    "Upgrade:websocket\r\n"
    "Connection:Upgrade\r\n"
    "Sec-WebSocket-Accept:{0}\r\n"
    "WebSocket-Location:ws://{1}{2}\r\n\r\n"
)


class WebSocketClientConnection(WebSocketProtocol):
    """WebSocket Server's Client Connection"""

    client: socket.socket = None
    client_address: str = ""

    lock = Lock()
    closed = False

    def __init__(self, client: socket.socket, client_address: str):
        self.client = client
        self.client_address = client_address

    def __str__(self):
        return "<client:%s>" % self.address

    @property
    def address(self):
        return f"%s:%d" % self.client_address

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

        self.client.settimeout(1)
        while True:
            with self.lock:
                if self.closed:
                    break

                try:
                    try:
                        data = self.client.recv(self.buffer_size)
                    except socket.timeout:
                        self.ping()
                        continue
                except KeyboardInterrupt:
                    break

            if data:
                log.info(f"{self} recv {data!r}")
                frame = self.unpack_data_to_frame(data)
                self.handle_frame(frame)

    def handshake(self) -> bool:
        data = self.client.recv(self.buffer_size)
        log.info(f"{self} recv {data!r}")

        headers = parse_http_headers(data.decode("utf-8"))
        response = websocket_upgrade_template_server.format(
            base64.b64encode(
                hashlib.sha1(
                    (headers["Sec-WebSocket-Key"] + self.GUID).encode("utf-8")
                ).digest()
            ).decode("utf-8"),
            headers["Host"],
            headers["Path"],
        ).encode("utf-8")

        self._send(response)

        return True

    def _send(self, data):
        log.info(f"{self} will send {data!r}")
        self.client.send(data)

    def send_message(self, message):
        pass


class WebSocketServer(object):
    """WebSocket Protocol Implementation for Server."""

    server: socket.socket = None
    should_close: bool = False

    def __init__(self, host: str = "localhost", port: Union[str, int] = 8089):
        self._host, self._port = host, port

    def __str__(self):
        return "<server:%s>" % self.address

    @property
    def address(self):
        return f"{self._host}:{self._port}"

    def listen_and_serve(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self._host, self._port))
        self.server.listen(5)

        log.info(f"listening on {self.address}")

        ts: list[Thread] = []
        clients: list[WebSocketClientConnection] = []

        # If you do not set a timeout, it will block forever and no operation can be interrupted
        self.server.settimeout(1)
        while not self.should_close:
            try:
                try:
                    client, client_address = self.server.accept()
                except socket.timeout:
                    continue
            except KeyboardInterrupt:
                break

            client_connection = WebSocketClientConnection(client, client_address)
            clients.append(client_connection)

            log.info(f"connected by {client_connection}")

            t = Thread(target=client_connection.serve, daemon=True)
            ts.append(t)
            t.start()

        for client in clients:
            client.close()

        for t in ts:
            t.join()

        self.close()

    def close(self):
        log.info(f"close {self}")
        self.server.close()
        log.info(f"{self} closed")


if __name__ == "__main__":
    server = WebSocketServer()
    server.listen_and_serve()
