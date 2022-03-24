'''
Date: 2021.11.15 12:57
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2021.11.15 12:57
'''
import socketserver
import socket
from protocol import Parser
from binascii import unhexlify
from pkgs.logger import log


class RequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        client: socket.socket = self.request
        address = self.client_address
        parser = Parser(client)

        log.debug('Connected by %s:%d.' % address)

        while True:
            try:
                recv = client.recv(1024)
                if recv:
                    log.info(f'[recv] {repr(recv)}')
                    parser.put(unhexlify(recv))
            except ConnectionError:
                break

        log.debug('Disconnected by %s:%d.' % address)


if __name__ == '__main__':
    import config

    server = socketserver.ThreadingTCPServer((config.TCP_HOST, config.TCP_PORT), RequestHandler)
    server.serve_forever()
