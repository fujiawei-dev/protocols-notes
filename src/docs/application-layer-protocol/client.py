'''
Date: 2021.11.15 13:58
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2021.11.15 13:58
'''
import socket
import config
from time import sleep

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    # Connect to server and send data
    client.connect((config.TCP_HOST, config.TCP_PORT))

    while True:
        client.sendall(b'7e0102000573608155441500015091529468fe7e')
        client.sendall(b'7E010000307360802475620000000000004A435A4E53476574636861726D736D'
                       b'61727430303030303030433132303030300056494E0000000000000000A47E')
        client.sendall(b'7E0102000573608024756200014900624645A47E')
        client.sendall(b'7E0200001C73608024756200100000000000100003015834BA06C9D86B002000000124181219164655E27E')
        client.sendall(b'7E000200007360802475620010E27E')

        # Receive data from the server and shut down
        received = client.recv(1024)
        print("Received: {}".format(received))

        sleep(3)
