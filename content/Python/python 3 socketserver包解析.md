 Python 3 socketserver 包解析
 2018-05-22
tags: python, socket, socket server



`socketserver` 包实现了简单的 `socket` 通信任务. 一共有 4 种基础通信服务: `TCPServer`, `UDPServer`, `UnixStreamServer`, `UnixDatagramServer`. 基于 tcp/udp, unix stream 的. 这 4 种是同步的, 另外有基于进程和线程服务混合类可用来实现异步(多线程/多进程)服务器, `ForkingMixIn` 只能用于支持 POSIX 系统, `ThreadingMixIn` 可用于线程服务器. 

包内实现了基础的异步(多线程/多进程)服务器示例 `ForkingTCPServer`, `ForkingUDPServer`, `ThreadingTCPServer`, `ThreadingUDPServer`. 要注意, 如果实现自己的异步服务器, 继承顺序要先继承 mixin 类再继承 server 类, mixin 类中覆盖了 如 `class ForkingTCPServer(ForkingMixIn, TCPServer)`

主要类的基本继承:

```
+------------+
| BaseServer |
+------------+
      |
      v
+-----------+        +------------------+
| TCPServer |------->| UnixStreamServer |
+-----------+        +------------------+
      |
      v
+-----------+        +--------------------+
| UDPServer |------->| UnixDatagramServer |
+-----------+        +--------------------+
```

### 1. `BaseServer` 解析



































