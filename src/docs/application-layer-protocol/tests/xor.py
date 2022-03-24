'''
Date: 2021.11.15 14:59
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2021.11.15 14:59
'''
from binascii import unhexlify

from protocol import Parser

body = unhexlify(b'0102000573608155441500015091529468')  # fe
body = unhexlify(b'8001000573608024756200000010000200')

body = bytearray([0x30, 0x7e, 0x08, 0x7d, 0x55])  # 7e307d02087d01557e
Parser.parse(unhexlify(Parser.combine(body)))
