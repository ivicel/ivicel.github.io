title: 基于 uwsgi 的实现 flask 的 websocket 连接 -- steamkey 的移植
date: 2018-9-10
tags: python, flask, websocket, steam, steamkey



[steam-key-python](https://github.com/ivicel/steam-key-python) 是 [steam-key](https://github.com/zyfworks/steam-key) 的python 移植, 原开发基于 node.js.

使用到的主要开发包:

* [steam](https://github.com/ValvePython/steam) 一个用 python 实现的 steamkit
* flask web 框架
* gevent 异步框架
* uwsgi 后端 server

##### 1. flask 结合 websocket 问题

 根据 Websocket 协议, 从 HTTP 升级到 Websocket 要发送以下 GET 请求, 来协商

```
GET /websocket HTTP/1.1
Connection: Upgrade
Upgrade: websocket
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: KSk4Wty1NJInqzWMBbQqCQ==
```

当我们收到这个请求时, 返回一个 response 来确定升级到

```
HTTP/1.1 101 Switching Protocols
Server: nginx/1.15.3
Date: Thu, 13 Sep 2018 05:56:14 GMT
Connection: upgrade
Upgrade: websocket
Sec-WebSocket-Accept: B1HnOTYR2fZO2PT0y6LImuBQtzQ=
```

要让 flask 支持 websocket, 就要做到两点.

1. 获得原始的 TCP 连接, 而我们的 WSGI 程序获得的是只要环境变量和一个回调函数, 如 `def application(environ, start_response)`. 这样的话, 我们可以在最底层的 `middleware` 里把 socket 连接放到 environ 变量中, 比如 `environ['socket']`, 这样无论我们在哪一个中间件里都可以处理到最原始的连接. 
2. 在获得到 TCP 连接后, 由于 Websocket 是基于 message 而不是基于 stream 的, 我们还需要实现 websocket 协议, 接管请求到 `/websocket` 的连接, 比如 ping/pong, send/receive

以上两点 uWSGI 已经帮我们实现好, 在 [uWSGI 文档](https://uwsgi-docs.readthedocs.io/en/latest/WebSockets.html)中提到了当使用 `--http-socket ` 参数来运行的 wsgi 应用时, 只要我们检查 `environ['HTTP_SEC_WEBSOCKET_KEY']` 变量, 这是升级到 websocket 里的请求, 便可知道该连接之后想升级到 websocket. uWSGI 已经帮我们把实现了 websocket 协议, 我们只要使用以下几个接口即可

```python
# 确定发回 Connection upgrade
uwsgi.websocket_handshake([key, origin, proto])

uwsgi.websocket_recv()
uwsgi.websocket_send(msg)
uwsgi.websocket_send_binary(msg) (added in 1.9.21 to support binary messages)
uwsgi.websocket_recv_nb()
uwsgi.websocket_send_from_sharedarea(id, pos) 
```

##### 2. flask 和 gevent 问题

Flask 是同步执行的, 我们主要的请求都在 websocket 中, 所以我们只在每一个 websocket upgrade request 中 patch 所有的 socket 即可. 



##### 3. 代码实现

前面说到, 因为要检测 `environ` 的值, 我们可以使用一个中间件 `WebsocketMiddleware`, 这样当我们生成 `ws = Websocket(app)`, 然后使用 `@ws.route('/ws')` 时便说明, url `/ws` 使用 websocket 连接.

```
uWSGI ------ Websocket Middleware ---if is websocket---> Websocket Application 
					 |
                     | else
                     |
              Flask Application
```

查看 flask 的源码可以看到在类 Flask 的最终实现 wsgi 协议的是方法 `wsgi_app()`, 并且源码里也说明了最好的中间件实现方式. 

```python
# 简化实现说明
from flask import Flask
from .websocket import Websocket

app = Flask(__name__)
# websocket_application
ws = Websocket(app)

@app.route('/')
def index():
    return re

# 我们会把 websocket 连接对象传给处理函数
# ws 参数是一个按 websocket 标准接口实现的包装对象
# 只需按标准接口调用
@ws.route('/ws')
def websocket_connect(ws):
    while not ws.closed:
        msg = ws.receive()
        print('receive message: {!r}'.format(msg))
        ws.send(msg)

```

主要类的实现, `Websocket` 类实现了一个 WGSI 协议, 接收从 uWSGI 的回调, 然后将请求放到 `WebsocketMiddleware` 中判断是否为 websocket, 不是的话发送到 flask application 来处理

```python
import uwsgi
import gevent
from gevent.queue import Empty, Queue
from gevent.event import Event
from gevent.select import select as gselect
from gevent.monkey import patch_all
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
        
# Websocket 类
class WebSocket(object):
    def __init__(self, app):
        # 路由表
        self.url_map = Map()
        # 路由处理函数
        self.view_functions = {}
        # 在这里将 wsgi 应用设置为 WebSocketMiddleware
        # 并且我们还保留了原 Flask.wsgi_app 的引用
        app.wsgi_app = WebSocketMiddleware(app.wsgi_app, self)

    def add_url_map(self, url, endpoint=None, view_func=None, **options):
        """添加到路由表"""
	
    def route(self, rule, **options):
        """路由表"""
        
        
# WebSocketMiddleware 类
class WebSocketMiddleware(object):
    def __init__(self, wsgi_app, websocket):
        # Fask application
        self.wsgi_app = wsgi_app
        # Websocket application
        self.ws = websocket

    def __call__(self, environ, start_response):
        # 当请求到达时, 我们先判断该路由是否在 websocket 中绑定了
        adapter = self.ws.url_map.bind_to_environ(environ)
        try:
            endpoint, args = adapter.match()
            handler = self.ws.view_functions[endpoint]
        except HTTPException:
            handler = None
		# websocket 的升级判断, 失败则使用 flask application 处理
        if handler is None or 'HTTP_SEC_WEBSOCKET_KEY' not in environ:    
            return self.wsgi_app(environ, start_response)
        
		# 回应客户端升级协议到 websocket
        uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))
		
        # 使用 gevent 来处理, 发送消息的触发事件和队列
        send_event = Event()
        send_queue = Queue()
		# 接收消息的触发事件和队列
        recv_event = Event()
        recv_queue = Queue()
        
		# WebSocketWrapper 是一个包装类, 提供了众所周知的 websocket 接口
        client = WebSocketWrapper(environ, uwsgi.connection_fd(), send_event,
                                  send_queue, recv_event, recv_queue, self.ws.timeout)
		
        def listener(client):
            gselect([client.fd], [], [])
            recv_event.set()
            
		# handler 是我们的设置的路由函数, 在这我们派生出的 greenlet object 并把 weboscket wrapper 传给它
        handler = gevent.spawn(handler, client, *args)
        # 设置当 socket 可读, 也即是有消息从客户端发过来时的回调
        listening = gevent.spawn(listener, client)
        while True:
            if client.closed:
                recv_queue.put(None)
                listening.kill()
                handler.join(client.timeout)
                return ''
            
			# 一是路由回调需要发送消息, 消息会被加到发送队列等待发送
            # 二是发送队列里有消息需要发送
            # 三是从客户端那收到消息
            gevent.wait([handler, send_event, recv_event], None, 1)

            # 有消息需要发送
            if send_event.is_set():
                try:
                    while True:
                        msg = send_queue.get_nowait()
                        uwsgi.websocket_send(msg)
                except gevent.queue.Empty:
                    send_event.clear()
                except IOError:
                    client.closed = True
            elif recv_event.is_set():    # 接收到消息
                recv_event.clear()
                try:
                    message = uwsgi.websocket_recv_nb()
                    while message:
                        recv_queue.put(message)
                        message = uwsgi.websocket_recv_nb()
                    listening = gevent.spawn(listener, client)
                except IOError:
                    client.closed = True

            elif handler.ready():
                listening.kill()
                return ''
```



完整代码在: https://github.com/ivicel/steam-key-python



#### Reference

1. https://uwsgi-docs.readthedocs.io/en/latest/WebSockets.html

2. https://github.com/zeekay/flask-uwsgi-websocket/