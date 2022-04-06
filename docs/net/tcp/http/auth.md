---
date: 2022-04-06T10:00:24+08:00
author: "Rustle Karl"

title: "HTTP Basic 和 Digest 认证介绍与计算"
url:  "posts/protocols/docs/net/tcp/http/auth"  # 永久链接
tags: [ "Protocols", "README" ]  # 标签
series: [ "Protocols 学习笔记" ]  # 系列
categories: [ "学习笔记" ]  # 分类

toc: true  # 目录
draft: false  # 草稿
---

## 协议原文参考

```shell
https://tools.ietf.org/html/rfc2617
```

## Basic 认证形式

### Basic认证请求示例

```
GET / HTTP/1.1
Host: 192.168.220.128
Authorization: Basic YWRtaW46MTIzNDU2
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0
Accept-Encoding: gzip, deflate
Accept: */*
Cache-Control: no-cache
Cookie: Secure
Connection: close
```

### Basic 认证计算方法

前边请求 Authorization 头的 YWRtaW46MTIzNDU2，实际上是用户名 admin 密码 123456 使用以下计算方法得到：

```
base64(username:password)
```

Python 计算代码如下：

```python
import base64

def get_basic_authorization_header_value(username,password):
    # base64编码前后都（要）是字节码形式
    authorization_value = base64.b64encode((f"{username}:{password}").encode()).decode()
    authorization_header_value = f"Basic {authorization_value}"
    return authorization_header_value
```

## Digest 认证形式

### Digest 认证请求示例

```
GET / HTTP/1.1
Host: 192.168.220.128
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0
Authorization: Digest username="admin",realm="TVT API Test Tool",nonce="d4f95e85dc5a39a4914db61b67878f5b",uri="GetDeviceInfo",algorithm="MD5",cnonce="d4f95e85dc5a39a4914db61b67878f5b",nc=00000001,qop="auth",response="1cc4cf126d3c4a70d2de34c5d8c2943c"
Accept-Encoding: gzip, deflate
Accept: */*
Cache-Control: no-cache
Cookie: Secure
Connection: close
```

- username 系统用户名；客户端自行填充
- realm 领域；服务端通过 WWW-Authenticate 头返回内容可以自己随便定，但其目的是用于提示客户端当前是什么系统，所以规范来说应类似于“myhost@testrealm.com”的形式。
- nonce 服务端通过 WWW-Authenticate 头返回的随机数
- uri 请求接口或资源（似乎规范来说应用 GET 或 POST 后的一样，上边例子中少了 / 是因为服务端没按规范实现）
- algorithm 后边 response 用的计算方法
- cnonce client nonce，客户端生成的随机数
- nc nonce count，用于标识进行请求的次数。（但你一直不变服务端也不会管你对不对）
- qop quality of protection，进一步限定 response 的计算方法，服务端通过 WWW-Authenticate 头返回。
- response 认证最主要的值，前面各字段除 algorithm 外全要参与该值的计算。

### Digest 认证计算方法

在最开始的[RFC 2069](https://tools.ietf.org/html/rfc2069)中规定 response 计算方法如下：

```
HA1 = MD5(username:realm:password)
HA2 = MD5(method:uri)
response = MD5(HA1:nonce:HA2)
```

随后的[RFC 2617](https://tools.ietf.org/html/rfc2617)对计算方法进行了增强，规定计算方法如下（当 algorithm 值为 MD5 或未指定、qop 未指定时等同 RFC 2069）：

```
# HA1部分
# 当algorithm值为"MD5"或未指定时，HA1计算方法如下
HA1 = MD5(username:realm:password)
# 当algorithm值为"MD5-sess"时，HA1计算方法如下
HA1 = MD5(MD5(username:realm:password):nonce:cnonce)

# HA2部分
# 当qop值为"auth"或未指定时，HA2计算方法如下
HA2 = MD5(method:uri)
# 当qop值为"auth-int"时，HA2计算方法如下；entityBody是指整个请求body，未经压缩等处理之前
HA2 = MD5(method:uri:MD5(entityBody))

# response部分
# 当qop值为"auth"或"auth-int"时，response计算方法如下
response = MD5(HA1:nonce:nonceCount:cnonce:qop:HA2)
# 当qop未指定时，response计算方法如下
response = MD5(HA1:nonce:HA2)
```

Python 计算代码如下：

```python
import hashlib

# body初始值不要是None，不然下边encode时会报错
def get_basic_authorization_header_value(username, password, uri, method, realm, nonce, nc, cnonce, algorithm=None, qop=None, body=""):
    response_value = calc_digest_response_value(username, password, uri, method, realm, nonce, nc, cnonce, algorithm, qop, body)
    authorization_header_value = f'Digest username="{username}",realm="{realm}",nonce="{nonce}",uri="{uri}",algorithm="{algorithm}",cnonce="{cnonce}",nc={nc},qop="{qop}",response="{response_value}"',
    return authorization_header_value

def calc_digest_response_value(username, password, uri, method, realm, nonce, nc, cnonce, algorithm=None, qop=None, body=""):
    # HA1部分
    # 当algorithm值为"MD5"或未指定时，HA1计算方法如下
    if algorithm == "MD5" or algorithm == "" or algorithm is None:
        HA1 = hashlib.md5((f"{username}:{realm}:{password}").encode()).hexdigest()
    # 当algorithm值为"MD5-sess"时，HA1计算方法如下
    elif algorithm == "MD5-sess":
        HA1 = hashlib.md5((f"{username}:{realm}:{password}").encode()).hexdigest()
        HA1 = hashlib.md5((f"{HA1}:{nonce}:{cnonce}").encode()).hexdigest()
    else:
        response_value = '"the value of algorithm must be one of "MD5"/"MD5-sess"/""/None'
        return response_value

    # HA2部分
    # 当qop值为"auth"或未指定时，HA2计算方法如下
    if qop == "auth" or qop == "" or qop is None:
        HA2 = hashlib.md5((f"{method}:{uri}").encode()).hexdigest()
    # 当qop值为"auth-int"时，HA2计算方法如下；entityBody是不是指整个body我其实不太确定
    elif qop == "auth-int":
        HA2 = hashlib.md5((f"{body}").encode()).hexdigest()
        HA2 = hashlib.md5((f"{method}:{uri}:{HA2}").encode()).hexdigest()
    else:
        response_value = '"the value of qop must be one of "auth"/"auth-int"/""/None'
        return response_value

    # response部分
    # 当qop值为"auth"或"auth-int"时，response计算方法如下
    if qop == "auth" or qop == "auth-int":
        response_value = hashlib.md5((f"{HA1}:{nonce}:{nc}:{cnonce}:{qop}:{HA2}").encode()).hexdigest()
    # 当qop未指定时，response计算方法如下
    elif qop == "" or qop is None:
        response_value = hashlib.md5((f"{HA1}:{nonce}:{HA2}").encode()).hexdigest()
    else:
        response_value = "unknown error"
    return response_value
```

## 请求客户端

```python
import requests
from requests.auth import HTTPDigestAuth

requests.put(
    "http://localhost:8787/immigration/debug",
    auth=HTTPDigestAuth("admin", "admin"),
    json={"x": "y"},
)
```

## Go 中间件实现

见源码。
