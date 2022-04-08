---
date: 2022-04-08T11:41:02+08:00
author: "Rustle Karl"

title: "NTP 网络时间协议"
url:  "posts/protocols/docs/net/udp/ntp"  # 永久链接
tags: [ "Protocols", "README" ]  # 标签
series: [ "Protocols 学习笔记" ]  # 系列
categories: [ "学习笔记" ]  # 分类

toc: true  # 目录
draft: false  # 草稿
---

## 协议原文参考

```shell

```


### SNTP 简单网络时间协议

```shell
import socket
import struct
import time

TIME1997 = 2208988800
NTP_SERVER = "pool.ntp.org"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = b"\x1b" + 47 * b"\0"
client.sendto(data, (NTP_SERVER, 123))
data, address = client.recvfrom(1024)
print("response received from server:", address)

ts = struct.unpack("!12L", data)
t = ts[10]
t -= TIME1997
print(time.ctime(t))
```

```shell

```


## 协议原文参考

```shell

```

## 二级

### 三级

```shell

```

```shell

```


## 协议原文参考

```shell

```

## 二级

### 三级

```shell

```

```shell

```


## 协议原文参考

```shell

```

## 二级

### 三级

```shell

```

```shell

```


## 协议原文参考

```shell

```

## 二级

### 三级

```shell

```

```shell

```


