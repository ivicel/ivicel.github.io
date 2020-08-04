---

title: "RTFSC: Flask 的源码阅读(一)"
date: 2018-09-18
tags: ["flask", "python", "源代码阅读", "RTFSC"]
categories: ['Python']

---



> 使用自带的单线程 server 看源码

#### 1. 从 WSGI 开始

一个最简单的 Flask 程序

```python
from flask import Flask

app = Flask(__file__)

@app.route('/')
def index():
    return 'Hello, world'

if __name__ == '__main__':
    app.run()
```

在 `run()` 方法中可以看到调用了 `werkzeug.serving.run_simple()` 来运行, 传入的的 `WSGI` 应用就是 `self` 也就是 `Flask` 对象. 根据 `WSGI` 协议, 其必定是一个 `callable_appliaction(environ, start_response)`. 所以下来查看类对象的 `__call__()` 方法. 可以看到真正的 `WSGI` 定义是 `Flask.wsgi_app()` 方法. 

代码文档也说明了这样定义的原因, 就是方便我们使用时做 `Middleware`, 只要 

```python
app.wsgi_app = MyMiddleware(app.wsgi_app)
```

这样我们依旧还能使用 `Flask` 来方便的处理各种 HTTP 请求.

```python
def wsgi_app(self, environ, start_response):
    # 生成请求上下文
    ctx = self.request_context(environ)
    error = None
    try:
        try:
            # 将其入栈
            ctx.push()
            # 派发请求 url 到对应的处理方法中
            response = self.full_dispatch_request()
        except Exception as e:
            # 属于 HTTP 错误, 记录出错情况, 404, 501, 403...
            error = e
            response = self.handle_exception(e)
        except:
            # 系统程序错误
            error = sys.exc_info()[1]
            # 向上抛, 告知 WSGI server 程序产生了错误
            raise
        # 有 HTTP 返回结果
        return response(environ, start_response)
    finally:
        # 
        if self.should_ignore_error(error):
            error = None
        # 请求完毕时, 将请求出栈
        ctx.auto_pop(error)
```

#### 2. 请求上下文都初看

在进入到 WSGI 之后, 根据传入的环境变量 `environ` 生成一个请求上下文对象 `RequestContext`, 调用对象的 `push` 方法.

根据类的文档, 上下文把当前请求相当的东西都压入栈,  然后在请求完毕的时候把这些都出栈. 这个栈指的就是 `flask.global._request_ctx_stack`, 并且在弹出栈时, 调用所有在 `flask.Flask.teardown_request` 的注册方法.

```python
class RequestContext(object):
    def __init__(self, app, environ, request=None):
        # app 就是 Flask() 对象
        self.app = app
        # 默认的 flask.wrapper.Request 实现是从 werkzeug.wrappers.Request 继承 
        # 这样方便我们自己实现自己的 Request
        if request is None:
            request = app.request_class(environ)
        self.request = request
        # 创建一个 werkzeug.routing.MapAdapter 用于检测匹配 url
        self.url_adapter = app.create_url_adapter(self.request)
        self.flashes = None
        self.session = None
        self._implicit_app_ctx_stack = []
        self.preserved = False
        self._preserved_exc = None
        self._after_request_functions = []
        # 在这里对 url 进行了匹配
        # self.request.url_rule 保存了匹配的 url
        # self.request.view_args 保存了匹配的 query_args
        # 匹配失败的话, self.request.routing_exception 保存了异常对象
        self.match_request()
```

#### 3. 所以什么是上下文: RequestContext, AppContext

flask 中实现了两个全局的上下文栈, `flask.globals` 文件内

1) 请求上下文 `_request_ctx_stack`, 用来保存每一次 `HTTP Request` 的大部分信息, 每次请求开始时都会压入栈中, 在请求结束时被弹出栈. 

2) 应用上下文, 根据 `WSGI` 协议, `WSGI` 分为 `Server`, `Client`, `Middleware` 三种部件, 但这三种限定也是模糊的. 只要实现 `S` 和 `C` 端两个方向的都可以叫 `Middleware`. 所以我们可以把 `Flask` 请求再一次传给另一个 `WSGI Application` 来处理, 比如 `Django` 或者多个 `Flask` 程序, 或者处理完成再返还给 `Flask`, 这就有一个应用上下文. 而 flask 自己的应用上下文是在第一次收到 `request` 的时候生成的.

上下文指的是, 简单理解就是记录**一定区域内的信息**, 离开这个区域, 这个信息就不存在了, 在这个区域内保证了一定的操作. 比如`with open`, 我们可以保证 打开/关闭 操作, 在这之内是 可读/可写 的. 

`Flask` 内实现的上下文其实只是一个 Python 字典, 字典每一个值就对应一个 stack, 是一个 list. 因为请求是并发/并行的, 也有可能多个应用程序在同时运行.  所以字典的 key 是一个需要能区分不同线程/进程的值.

```python
try:
    # 首选 greenlet 的当前运行 greenlet 对象的标识符
    from greenlet import getcurrent as get_ident
except ImportError:
    # 没有安装 greenlet 时, 使用当前线程的 thread_local 标识, 注意 py2/3 的兼容
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident
```

两个上下文都是一个栈, 都定义在 `flask.globals`

```python
_request_ctx_stack = LocalStack()
_app_ctx_stack = LocalStack()
```

栈的实现在 `werkzeug.local` 中

```python
class Local(object):
    """
    	实际底层的数据实现, 使用 __slots__ 避免占用大量内存
    	__storage__ 为实际储存数据的字典
    	__ident_func__ 为 __storage__ 的 key
    	实现了一些 magic method 都很简单, 主要是要 get_ident
    """
    __slots__ = ('__storage__', '__ident_func__')

    def __init__(self):
        object.__setattr__(self, '__storage__', {})
        object.__setattr__(self, '__ident_func__', get_ident)

    def __iter__(self):
        return iter(self.__storage__.items())

    def __call__(self, proxy):
        """Create a proxy for a name."""
        return LocalProxy(self, proxy)

    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)
	# 因为我们把数据存储到 __storage__ 中, 对应的 setter, getter 方法
    def __getattr__(self, name):
        try:
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__ident_func__()
        storage = self.__storage__
        # 每个独立的线程或者 greentlet 对象都有一个保存自己的字典
        # 比如在多线程状态下多个 request 时, 就有
        # 每个 request 都在 storage[thread_identification] = {'request': value}
        # 注意存进来的 name 其实是最后的 key
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}

    def __delattr__(self, name):
        try:
            del self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)


class LocalStack(object):
    """
		栈的实现, 回过来看
		请求上下文: _request_ctx_stack = LocalStack()
		应用上下文: _app_ctx_stack = LocalStack()
    """

    def __init__(self):
        self._local = Local()

    def __release_local__(self):
        self._local.__release_local__()

    def push(self, obj):
        """
        	当在 RequestContext 里调用 _request_ctx_stack.push 时, 也就是相当
			Local.__storage__[Local.__ident_func__()]['stack'] = [RequestContext()]
			对于 _app_ctx_stack, 就是存了 AppContext 对象而已
        """
        rv = getattr(self._local, 'stack', None)
        if rv is None:
            self._local.stack = rv = []
        rv.append(obj)
        return rv

    def pop(self):
        """
        	弹出栈顶元素, 当最后只有一个元素在栈中的时候, 这时再弹出元素时, 会把这个栈置为 None
        	原因应该是因为这个实现 Request 也是要用的, 请求结束了, 这线程也不需要了
        	最终调用的是 Local.__release_local__
        	其实就是 __storage__.pop(__ident_func__(), None)
        """
        stack = getattr(self._local, 'stack', None)
        if stack is None        if stack is None:
            return None
        elif len(stack) == 1:
            release_local(self._local)
            return stack[-1]
        else:
            return stack.pop()

    @property
    def top(self):
        """返回栈顶"""
        try:
            return self._local.stack[-1]
        except (AttributeError, IndexError):
            return None

```

上下文其实是很简单的结构, 关键是怎么使用, 回过来, 我们知道, 请求到来时, 使用环境变量生成了一个请求上下文, 然后调用了对象的 `RequestContext.push()` 方法

```python
class RequestContext(object):
    def push(self):
        # 查找当前请求栈中顶端的请求, 这里的 top 是 RequestContext 对象, 第一次为 None,
        top = _request_ctx_stack.top
        # RequestContext.preserved 代表这个请求是否保留,
        # 在下一个请求(同一线程中)到来时, 把保留的请求弹出
        if top is not None and top.preserved:
            top.pop(top._preserved_exc)
		# 确保这个请求栈带有应用上下文 AppContext 对象
        # 如果请求被保留的话那么 app_ctx 不为 None, 这时我们就不再创建新的 AppContext
        app_ctx = _app_ctx_stack.top
        if app_ctx is None or app_ctx.app != self.app:
            app_ctx = self.app.app_context()
            app_ctx.push()
            self._implicit_app_ctx_stack.append(app_ctx)
        else:
            self._implicit_app_ctx_stack.append(None)
		# py3 移除了该方法, 清除当前线程的 exception 信息
        if hasattr(sys, 'exc_clear'):
            sys.exc_clear()
		# 压入 Request 栈中
        _request_ctx_stack.push(self)
		# 第一次请求时, 创建一个新的 session
        if self.session is None:
            session_interface = self.app.session_interface
            self.session = session_interface.open_session(
                self.app, self.request
            )
			# 默认的 session 是实现在内存中的 python 对象
            # 当网站并发达到一定规模或者需要分布式时, 我们也可以使用 redis 这样的数据库来实现
            if self.session is None:
                self.session = session_interface.make_null_session(self.app)

```

这样我们就清楚了, `_request_ctx_stack` 为我们保存了每一次的请求对象, 而且这个 `RequestContext` 对象还有对应指 `WSGI` 应用上下文, 存在对应的 `_app_ct_stack` 相同的线程标识符里的字典. 另外还有从客户端发过来的对应 `session` 信息, 这样回应一个请求的信息都具备完了.







#### Reference:

1. https://github.com/pallets/flask
2. https://github.com/pallets/werkzeug
3. http://flask.pocoo.org
4. http://werkzeug.pocoo.org