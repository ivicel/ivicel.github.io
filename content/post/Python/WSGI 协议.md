---

title: "WSGI 协议"
date: 2018-06-01
tags: ["wsgi", "python", "服务器", "协议", "web server"]
categories: ['Python']

---



#### 1. 简介

WSGI(Web Server Gateway Interface) 定义在 [PEP 3333](https://www.python.org/dev/peps/pep-3333/) 中, WSGI 不是要重新创造一个 web server 或者 framework, 而是定义一个标准接口, 实现这个标准接口的 web server 都可以通过该接口调用 python 程序, 从而使用 python 程序来处理网络数据, 然后再发回给 client.

WSGI 实现分为 client 端和 server 端, 并且 WSGI 是可以按层堆叠的, 中间层称为 middleware. middleware 其实质就是实现了 client, server 两种, 这样来看, 上层总是下层的 server, 下层是上层的 client.

#### 2. Client 端

client 端会从被 server 端调用, 所以传给 server 的必须是一个 `callable` 对象, 比如 `function`, `method`, `class`, 实现了 `__call__` 方法的对象实例, server 端不会假想 client 是怎么实现的, 是一个函数还是一个方法, 只知道这一定是 callable 的. 

server 调用时, 会传会 client 两个参数, 参数名不是固定的, 只是约定俗成而已. 以 `function` 来举例: 

```python
def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return [b'hello, world']
```

* `environ` 是一个 CGI-style  环境变量字典, 由 server 端来传递过, client 可以修改这个字典
* `start_response` 是 一个 server 端的一个回调方法, 用来设置返回的 http headers. 其方法定义为 `def start_response(status, response_headers, exec_info=None)`
  `status` 和 `response_headers` 是必须的, `status` 表示返回的状态码(string 类型), 比如 `"200 OK"`; `response_headers` 表示其他的头部信息, 使用一个列表表示, 列表中每一个都是一个 tuple`(header_name, header_value)`, 比如 `[('Content-Type', 'text/html'), ('Content-Length', 30)]`. `exec_info` 是可选的, boolean 值, 用来控制当发生错误时, 向浏览器发送错误消息
* client 要返回一个一 `iterable` 并且对于 python 3, `iterable` 内必须是 `bytes` 类型, 因为写入 socket 的是按字节写入的. 对于 python 2 来说便是 str 类型(在 python 2 中是 str 是字节类型). 通常我们会返回一个 list, 包含 bytes. 比如 `[b'Hello, world']`

#### 3. `environ` 参数

`environ` 参数是从 server 传过来的一些 CGI-style 字典. 

以下这些 key 是必须包含的, 如果 server 没有从浏览器中获取到对应的值, 则其值会是 empty string

* `REQUEST_METHOD`  请求方法, 如 `GET`, `POST`等 
* `SCRIPT_NAME`  The initial portion of the request URL's"path" that corresponds to the application object, so that the application knows its virtual "location". This **may** be an empty string, if the application corresponds to the "root" of the server.
* `PATH_INFO` 请求路径
* `QUERY_STRING` 查询键值对, 跟着 `?` 后的部分
* `CONTENT-TYPE` 对应头部中的 `Content-Type` 值, 可为空
* `CONTENT-LENGTH` 对应头部中的 `Content-Length` 值, 可为空
* `SERVER_NAME`, `SERVER_PORT` 服务器名和端口, 当存在 `HTTP_HOST`这个值时, `HTTP_HOST` 才是真正的指 服务器地址, 比如 ip, localhost, 域名等, 而这个值一般是一个别名, 比如 my_server_name 这样好记的名
* `SERVER_PROTOCOL` 请求的协议版本, 比如 `HTTP/1.1`, `HTTP/1.0`
* `HTTP_[Variables]` variables 代表了一系列的值, 这些值一般都是 http 的请求头部信息比如 `HTTP_USER_AGENT` 

另外还有一些值是可选, 为了兼容性, 不能假设非必须的值一定存在, 在使用非必须值前一定要先测试其值是否存在. 以上的值主要是关于请求的环境变量, WSGI 还要求了一些关于 server 的一些变量值, 也是必须要设置的.

* `wsgi.version` server 版本号
* `wsgi.url_scheme` url scheme, 比如 `http`, `https`
* `wsgi.input` 基于字节的 Input stream, 可以读取出浏览器发过来的请求体 body
* `wsgi.errors` 基于字符的 output stream, 写入错误信息, 以 `'\n'` 作为换行符, 一般传入 `sys.stderr` 或者错误日志文件
* `wsgi.multithread` 是否基于多线程
* `wsgi.multiprocess` 是否基于多进程
* `wsgi.run_once` application 是否只会被调用一次, 但即使为 `True` 也不能保证只运行一次



































