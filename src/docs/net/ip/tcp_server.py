"""
Date: 2022.04.03 16:48:45
LastEditors: Rustle Karl
LastEditTime: 2022.04.03 20:21:38
"""
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("0.0.0.0", 9090))
server.listen(50000)

while True:
    client, client_address = server.accept()
    client.send("OK")
