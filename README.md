---
date: 2022-03-11T18:07:18+08:00  # 创建日期
author: "Rustle Karl"  # 作者

# 文章
title: "Protocols 学习笔记"  # 文章标题
description: "纸上得来终觉浅，学到过知识点分分钟忘得一干二净，今后无论学什么，都做好笔记吧。"
url:  "posts/protocols/README"  # 设置网页永久链接
tags: [ "Protocols", "README" ]  # 标签
series: [ "Protocols 学习笔记" ]  # 系列
categories: [ "学习笔记" ]  # 分类

index: true  # 是否可以被索引
toc: true  # 是否自动生成目录
draft: false  # 草稿
---

# Protocols 学习笔记

> 纸上得来终觉浅，学到过知识点分分钟忘得一干二净，今后无论学什么，都做好笔记吧。

记录各种协议的学习笔记，比如 RFC 协议等。每种协议都至少用一种主流编程语言实现一遍。

## 目录结构

- `assets/images`: 笔记配图
- `assets/templates`: 笔记模板
- `docs`: 基础语法
- `libraries`: 库
  - `libraries/standard`: 标准库
  - `libraries/tripartite`: 第三方库
- `quickstart`: 基础用法
- `src`: 源码示例
  - `src/docs`: 基础语法源码示例
  - `src/libraries/standard`: 标准库源码示例
  - `src/libraries/tripartite`: 第三方库源码示例
  - `src/quickstart`: 基础用法源码示例

## 计算机网络

### IP

- [ICMP 协议详解](docs/net/ip/icmp.md)
- [TCP 协议详解](docs/net/ip/tcp.md)
- [用 Scapy 实现 TCP 握手协议](docs/net/ip/tcp_handshake.md)

### TCP

- [实现简单应用层协议的解析器](docs/net/tcp/application-layer-protocol.md)

#### HTTP

- [HTTP Basic 和 Digest 认证介绍与计算](docs/net/tcp/http/auth.md)
- [WebSocket 协议详解](docs/net/tcp/websocket.md)

### UDP

- [NTP 网络时间协议](docs/net/udp/ntp.md)
