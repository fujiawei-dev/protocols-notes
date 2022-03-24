'''
Date: 2021.11.15 14:32
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2021.11.15 14:32
'''
import struct
from binascii import unhexlify

header = b'020000347360802456680273'
obj = struct.unpack('>2H6BH', unhexlify(header))
obj[0], obj[1], bytearray(obj[2:8]).hex(), obj[8]

struct.pack('>2H6BH', 512, 45, *bytes.fromhex('736080245668'), 627).hex()
