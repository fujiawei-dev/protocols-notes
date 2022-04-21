"""
Date: 2022.04.03 16:59
Description: Omit
LastEditors: Rustle Karl
LastEditTime: 2022.04.03 16:59
"""
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import sr1

dst = "192.168.0.117"
dst = "192.168.0.106"
src = "117.127.1.231"
dport = 9090
sport = 9001

syn_packet = IP(dst=dst, src=src) / TCP(dport=dport, sport=sport, flags="S", seq=17)

syn_ack_packet = sr1(syn_packet)

ack_packet = IP(dst=dst) / TCP(
    dport=dport,
    sport=sport,
    flags="A",
    seq=18,
    ack=syn_ack_packet.seq + 1,
)

recv = sr1(ack_packet)
