---
date: 2022-03-25T07:30:47+08:00
author: "Rustle Karl"

title: "实现简单应用层协议的解析器"
url:  "posts/protocols/docs/net/tcp/application-layer-protocol"  # 永久链接
tags: [ "Protocols", "README" ]  # 标签
series: [ "Protocols 学习笔记" ]  # 系列
categories: [ "学习笔记" ]  # 分类

toc: true  # 目录
draft: false  # 草稿
---

## **1 定义协议**

协议，顾名思义，就是一种通信的约定，通信双方都能理解就行，我们可以定义复杂的协议，也可以定义简单的协议。本文在于讲解原理，定义一个几乎最简单的协议。格式如下：

```
开始字符1字节|整个报文长度4字节|序列号4字节|数据部分N字节|结束字符1字节
```

```javascript
// 开始标识符
const PACKET_START = 0x3;
// 结尾标识符
const PACKET_END = 0x4;
// 整个数据包长度
const TOTAL_LENGTH = 4;
// 序列号长度
const SEQ_LEN = 4;
// 数据包头部长度
const HEADER_LEN = TOTAL_LENGTH + SEQ_LEN;
```

## **2 解析协议**

本文是基于 TCP 的应用层协议，TCP 是面向字节流的协议，只负责透明传输字节，不负责解释字节，但是我们的数据包是有固定格式的，如果 TCP 把两个包放在一起传输，那我们如何识别呢？所以我们协议格式里，定义了开头和结束字符，一般定义一些特殊字符或者特殊格式为结束字符，这里我们定义的开始和结束字符是 0x3 和 0x4。所以我们要做的事情就是，判断 TCP 交给我们的字节流，根据开始和结束字符，逐个解析出我们的协议报文。

## **3 实现**

下面开始通过代码实现这个协议的解析。首先实现一个有限状态机。

```javascript
/**
 * 
 * @param {*} state 状态和处理函数的集合
 * @param {*} initState 初始化状态
 * @param {*} endState 结束状态
 */
function getMachine(state, initState, endState) {
    // 保存初始化状态
    let ret = initState;
    let buffer;
    return function(data) {
        if (ret === endState) {
            return;
        }
        if (data) {
            buffer = buffer ? Buffer.concat([buffer, data]) : data;
        }
        // 还没结束，继续执行
        while(ret !== endState) {
            if (!state[ret]) {
                return;
            }
            /*
                执行状态处理函数，返回[下一个状态, 剩下的数据]，
            */
            const result = state[ret](buffer);
            // 如果下一个状态是-1或者返回的数据是空说明需要更多的数据才能继续解析
            if (result[0] === -1) {
                return;
            }
            // 记录下一个状态和数据
            [ret, buffer] = result;
            if (!buffer.length) {
                return;
            }
        }
    }
}
```

因为解析的过程就是各种状态的转移和处理，所以用有限状态机来实现会清晰很多。上面的代码是一个小型的有限状态机框架。我们通过定义状态和对应的处理函数、开始状态、结束状态。然后得到一个状态机，就可以对输入的数据进行处理了。接下来我们定义一些数据结构。 定义一个表示数据包的类。

```javascript
// 表示一个协议包
class Packet {
    constructor() {
        this.length = 0;
        this.seq = 0;
        this.data = null;
    }
    set(field, value) {
        this[field] = value;
    }
    get(field) {
        return this[field];
    }
}
```

定义状态机状态和函数集

```javascript
// 解析器状态
const PARSE_STATE = {
  PARSE_INIT: 0,
  PARSE_HEADER: 1,
  PARSE_DATA: 2,
  PARSE_END: 3,
};
// 保存当前正在解析的数据包
var packet;
const STATE_TRANSITION = {
    [PARSE_STATE.PARSE_INIT](data) {
        if (!data || !data[0]) {
            return [-1, data];
        }
        if (data[0] !== PACKET_START) {
            return [-1, data ? data.slice(1) : data];
        }
        packet = new Packet();
        // 跳过开始标记符
        return [PARSE_STATE.PARSE_HEADER, data.slice(Buffer.from([PACKET_START]).length)];
    },
    [PARSE_STATE.PARSE_HEADER](data) {
        if (data.length < HEADER_LEN) {
          return [-1, data];
        }
        // 有效数据包的长度 = 整个数据包长度 - 头部长度
        packet.set('length', data.readUInt32BE() - HEADER_LEN);
        // 序列号
        packet.set('seq', data.readUInt32BE(TOTAL_LENGTH));
        // 解析完头部了，跳过去
        data = data.slice(HEADER_LEN);
        return [PARSE_STATE.PARSE_DATA, data];
    },
    [PARSE_STATE.PARSE_DATA](data) {
        const len = packet.get('length');
        if (data.length < len) {
            return [-1, data];
        }
        packet.set('data', data.slice(0, len));
        // 解析完数据了，完成一个包的解析，跳过数据部分和结束符
        data = data.slice(len);
        // 解析完一个数据包，输出
        return [PARSE_STATE.PARSE_END, data];
    },
    [PARSE_STATE.PARSE_END](data) {
        if (!data || !data[0]) {
            return [-1, data];
        }
        if (data[0] !== PACKET_END) {
            return [-1, data ? data.slice(1) : data];
        }
        console.log('parse success: ', packet);
        // 跳过开始标记符
        return [PARSE_STATE.PARSE_INIT, data.slice(Buffer.from([PACKET_START]).length)];
    },
};
```

这就是所有的代码。最后我们写两个测试用例玩一下。首先写一个服务器。

```javascript
const net = require('net');
const parse = require('./machine');
net.createServer(function(socket) {
  socket.on('data', function() {
    console.log('receiver: ', ...arguments)
    parse(...arguments);
  });
  socket.on('error', function() {
    console.log(...arguments)
  })
}).listen(10001);
```

然后写两个测试用例 用例一：正常发送

```javascript
const net = require('net');

async function test() {
  const socket = net.connect({port: 10001});
  socket.on('error', function() {
    console.log(...arguments);
  });
  let i = 0;
  const a = setInterval(() => {
    socket.write(Buffer.from([0x3,0x0, 0x0, 0x0, 0x9, 0x0, 0x0, 0x0, 0x1, i+1, 0x4]));
    i++ > 5 && (socket.end(), clearInterval(a));
  },1000)
}
test()
```

用例二：延迟发送

```javascript
const net = require('net');

async function test() {
  const socket = net.connect({port: 10001});
  socket.on('error', function() {
    console.log(...arguments);
  });
  let data = Buffer.from([0x3,0x0, 0x0, 0x0, 0x9, 0x0, 0x0, 0x0, 0x1, 0x1, 0x4]);
  let i = 0;
  const id = setInterval(() => {
      if (!data.length) {
        socket.end();
        return clearInterval(id);
      }
    const packet = data.slice(0, 1);
    console.log(packet)
    socket.write(packet);
    data = data.slice(1);
  }, 500);
}
test()
```

这就完成了一个应用层协议的实现和解析。
