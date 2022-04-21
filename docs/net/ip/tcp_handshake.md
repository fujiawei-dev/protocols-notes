---
date: 2022-04-03T18:57:43+08:00
author: "Rustle Karl"

title: "用 Scapy 实现 TCP 握手协议"
url:  "posts/protocols/docs/net/ip/tcp_handshake"  # 永久链接
tags: [ "Protocols", "README" ]  # 标签
series: [ "Protocols 学习笔记" ]  # 系列
categories: [ "学习笔记" ]  # 分类

toc: true  # 目录
draft: false  # 草稿
---

## 前言

Windows 上无法模拟，Windows 内核会在服务器回送 SYN_ACK 时，发送一个 RST 重置包，导致连接不成功，这是不可避免的，本质上，Scapy 在用户空间中运行，Windows 内核将首先接收到 SYN-ACK。在用 scapy 做任何事情之前，Windows 内核将发送一个 TCP RST。

所以发送一方只能是 Linux。至少两台 Linux，不能发给自己。

## TCP 接收方

### 启动一个基本的 TCP 服务器

```shell
nc -l -p 9090
```

### 监视连接情况

```shell
watch "netstat -an | grep 9090"
```

- SYN_RECV 已经收到 SYN 包
- ESTABLISHED 已经建立连接

### 端口占用

```shell
lsof -i:9090

netstat -tunlp | grep 9090
```

## TCP 发送方

### 修改防火墙

Scapy 可以发送原始的 TCP SYN 包，但是 Linux 内核（包括 Window 内核）不允许其他程序直接发送原始 TCP 报文，在程序发完之后，内核会立即发送一个 RST 包取消/中断这个不正常的连接。

为了避免这种情况，必须手动修改 Linux 的防火墙规则。

```shell
iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
iptables -L
```

### 启动 Scapy

```shell
scapy -H
```

```python
dst = "192.168.0.106"

syn_packet = IP(dst=dst) / TCP(dport=5555, sport=9000, flags="S", seq=17)

syn_ack_packet = sr1(syn_packet)

ack_packet = IP(dst=dst) / TCP(
    dport=5555,
    sport=9000,
    flags="A",
    seq=18,
    ack=syn_ack_packet.seq + 1,
)

sr1(ack_packet)
```

## 挥手协议

类似。
