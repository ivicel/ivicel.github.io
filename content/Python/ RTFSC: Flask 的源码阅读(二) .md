title: RTFSC: Flask 的源码阅读(二)
date: 2018-09-18
tags: flask, python, 源代码阅读, RTFSC



#### 1. 路由派发

由 `Flask.full_dispatch_request()` 发起路由派发

```python
def full_dispatch_request(self):
    # before_first_request 的回调
    self.try_trigger_before_first_request_functions()
    try:
        # signal 注册的回调
        request_started.send(self)
        # before_request 的回调, 在这我们也可以看到
        # 只有 before_request 回调中返回 None, 才继续向下派发
        rv = self.preprocess_request()
        if rv is None:
            rv = self.dispatch_request()
    except Exception as e:
        rv = self.handle_user_exception(e)
    return self.finalize_request(rv)
```

* 回调程序运行后, 第一次有 request 到达时的注册方法

在 `Flask.try_trigger_before_first_request_functions()` 运行我们在程序中使用 `before_first_request()` 注册的回调, 这是在程序运行时接收到第一次请求时调用, 可以注册多个回调方法, 检测第一次 request 只是使用了一个简单的标志位 `_got_first_request`.

**需要注意的是**

1. 回调这些方法的时, 使用了线程锁 `_before_request_lock` 在保证方法总是在回调用 reqeust 之前被调用, 想像一下多线程版本时, 可以同时到达多个 request. 
2. 在取得锁之后, 我们还在再次检查 `_got_first_request` 标志, 确保这些回调只调用过一次

```python
with self._before_request_lock:
    if self._got_first_request:
        return
    # before_first_request_funcs 是注册的方法列表
    for func in self.before_first_request_funcs:
        func()
    self._got_first_request = True
```

* 如果我们安装了 `blinker` , 这是一个同步的事件派发器, flask 为我们注册了一些事件, 像 `request-started`, `request-finished`, 以便我们在可以在程序外监听, 如果我们没有安装 `blinker`, 不会触发这些事件. 事件在 `flask.signals` 中

* 下来便是由 `url_value_request` 注册的回调和由 `before_request` 注册的回调. 前者是的回调方法里接收两个参数, 一是 `reqeust.endpoint` 这个默认就是方法的 `__name__`, 二是  `request.view_args` 这个是请求的参数 `query_string`.  前者回调存放在 `Flask.url_value_preprocessor`, 后者在 `Flask.before_request_func`

  这里需要注意的是我们有两个地方可以注册该事件, 一是全局 `Flask`, 二是 `Blueprint`. 这两种回调方法都存放在同一个变量中. 这是一个 dict, 全局的注册 `key` 为 `None`, 对 `Blueprint` 则是 blueprint 的名称为 `key`.

  > 对象 `before_request` , 当其中有方法返回非 `None` 时, 该 request 便返回给客户端了

* 下来派发到我们注册的路由方法

  ```python
  def dispatch_request(self):
      # Request 是从 werkzeug.wrapper.Reqeust 继承来的
      # 前面讲过, 当有 exception 时, exception 保存在 Request.routing_exception 中
      req = _request_ctx_stack.top.request
      if req.routing_exception is not None:
          # 抛出异常或者抛出调试异常
          self.raise_routing_exception(req)
  	# 没有问题
      rule = req.url_rule
  	# 我们在注册 view_func 时, 可以提供一个 provide_automatic_options 参数
      # 当这个为 True, 并且是 OPTIONS 请求时, 直接回复一个默认 option_response
      if getattr(rule, 'provide_automatic_options', False) \
         and req.method == 'OPTIONS':
          return self.make_default_options_response()
      # 终于来到我们自己注册的路由方法
      return self.view_functions[rule.endpoint](**req.view_args)
  
  def raise_routing_exception(self, request):
      # 非 debug 模式, 或者非重定向, 或是 (GET, HEAD, OPTIONS) 之一中的请求
      # 直接抛出
      if not self.debug \
         or not isinstance(request.routing_exception, RequestRedirect) \
         or request.method in ('GET', 'HEAD', 'OPTIONS'):
          raise request.routing_exception
  	# 在 debug 模式下, 抛出不同的输出, 也就是我们调试时看到调试页面
      from .debughelpers import FormDataRoutingRedirect
      raise FormDataRoutingRedirect(request)
  
  ```

#### 2. 请求异常处理

如果在请求处理是发生异常, 会抛到 `full_dispatch_request() ` 中, 在 `handle_user_exception()` 中处理

```python
def handle_user_exception(self, e):
    # 确保当前系统中刚发生的异常是原先我们捕捉到的异常
    # 如果不是的话, 那么向上 wsgi_app 中抛出 AssertionError
    # 由 handle_exception() 来处理
    exc_type, exc_value, tb = sys.exc_info()
    assert exc_value is e
    # BadRequestKeyError 指的是比如请求时需要提供某个参数, 但没有提供
    # 像 form 中 csrf_token, 那么会产生一个 KeyError, 而客户端则会收到一个 400 Bad Request
    if (
        (self.debug or self.config['TRAP_BAD_REQUEST_ERRORS'])
        and isinstance(e, BadRequestKeyError)
        # only set it if it's still the default description
        and e.description is BadRequestKeyError.description
    ):
        e.description = "KeyError: '{0}'".format(*e.args)
	# trap_http_exception 受到配置 'TRAP_HTTP_EXCEPTIONS', 这个会使用所有 exception 
    # 返回 True. 配置 'TRAP_BAD_REQUEST_ERRORS' 会单独捕捉 BAD_REQUEST
    if isinstance(e, HTTPException) and not self.trap_http_exception(e):
        # 默认的 http exception 处理.
        # 先查找注册的 error handler, 没有的话直接返回 exception 对象
        return self.handle_http_exception(e)
	# 查找注册了 error handler, 没有话重新抛出, 回到 handle_exception 处理
    handler = self._find_error_handler(e)
    if handler is None:
        reraise(exc_type, exc_value, tb)
    # handler() 要求返回的是一个 response
    return handler(e)
    
 def handle_exception(self, e):
    """默认的 exception 处理方法, 非 debug 模式下, 返回 500 Internal Server Error
       并记录到日志文件中
    """
    exc_type, exc_value, tb = sys.exc_info()
	# blinker 事件派发
    got_request_exception.send(self, exception=e)
    # 查找注册的 HTTP 状态处理方法, 404 500, 403 之类
    handler = self._find_error_handler(InternalServerError())
	# 查找配置文件 app.config 中 PROPAGATE_EXCEPTIONS, 向上抛出异常
    if self.propagate_exceptions:
        if exc_value is e:
            reraise(exc_type, exc_value, tb)
        else:
            raise e

    self.log_exception((exc_type, exc_value, tb))
    if handler is None:
        # 默认的 500
        return InternalServerError()
    # 使用我们自己的 500 处理方法
    return self.finalize_request(handler(e), from_error_handler=True)   
```

#### 3. 结束派发

如果我们在 `handle_user_exception` 不向上抛出异常, 将会运行到 `finalize_request()`

```python
def finalize_request(self, rv, from_error_handler=False):
    # 从 view_func 获得的正常 resepon 
    # 或者由捕获异常后, 生成的 404, 400, 500 之类的 response 对象
    response = self.make_response(rv)
    try:
        # 处理 after_request 注册的方法, 和 before_request 相同
        # 处理 session 相关, 把 session 发送到客户端
        response = self.process_response(response)
        # blinker 注册的事件
        request_finished.send(self, response=response)
    except Exception:
        # 从 handle_exception 过来的就是 True
        # # 从 handle_user_exception 过来就是 False, 那么就会抛到调用 Flask 应用的程序中
        if not from_error_handler:
            raise
        self.logger.exception('Request finalizing failed with an '
                              'error while handling an error')
    return response
```

返回到 `Flask.wsgi_app` 中, 然后依设置来决定是否弹出 `RequestContext`

```python
def auto_pop(self, exc):
    # 通过设置 flask._preserve_context 来保留 context
    # 出错了, 并且通过配置文件设置了 PRESERVE_CONTEXT_ON_EXCEPTION
    # 这个会下次 push 的时候被弹出
    if self.request.environ.get('flask._preserve_context') or \
       (exc is not None and self.app.preserve_context_on_exception):
        self.preserved = True
        self._preserved_exc = exc
    else:
        # 弹出 RequestContext 才会回调 teardown_request
        self.pop(exc)
        
def pop(self, exc=_sentinel):
    # 非保留情况下, 会每次新创建一个 AppContext 压入 _implicit_app_ctx_stack
    app_ctx = self._implicit_app_ctx_stack.pop()

    try:
        clear_request = False
        # 一般情况下 _implicit_app_ctx_stack 只有一个 AppContext, 上面已经弹出
        if not self._implicit_app_ctx_stack:
            self.preserved = False
            self._preserved_exc = None
            if exc is _sentinel:
                exc = sys.exc_info()[1]
            # app 级别的 teardown_request
            self.app.do_teardown_request(exc)
            if hasattr(sys, 'exc_clear'):
                sys.exc_clear()
			
            request_close = getattr(self.request, 'close', None)
            if request_close is not None:
                request_close()
            clear_request = True
    finally:
        rv = _request_ctx_stack.pop()

        # get rid of circular dependencies at the end of the request
        # so that we don't require the GC to be active.
        if clear_request:
            rv.request.environ['werkzeug.request'] = None

        # Get rid of the app as well if necessary.
        if app_ctx is not None:
            app_ctx.pop(exc)

        assert rv is self, 'Popped wrong request context.  ' \
            '(%r instead of %r)' % (rv, self)

```

如果在不保留 RequestContext 的话, 每次请求都会弹出 ReqeustContext 和 AppContext, 所以这也说明了如果我们在请求处理方法之外使用 RequestContext 或 AppContext 的话, 就会发生 Working outside of request context 这种情况.

#### 3. `request`, `current_app`, `g`, `session` 全局代理

从由 `_app_ctx_stack` 获得的,  这两个代理, 特别是 `g` 代理, 一般我们把一个全局的东西

* `current_app` 指向是当前的 `flask.app.Flask` 对象
* `g` 指向的是当前的 `flask.app.Flask` 对象 `g` 字典, 一般用来

当使用 `with Flask.app_context()` 的时候, 在 `with` 语句内 `current_app` 便会指向当前的 `Flask` 对象.  我们也知道在请求到来的时候, `RequestContext.push()` 也会把 `AppContext` 压入栈中, 此时 `current_app` 也是可以使用的. `g` 对象则是 `AppContext` 中的一个

```python
current_app = LocalProxy(_find_app)
g = LocalProxy(_partial(_loopku_app_object, 'g'))
```

从由 `_request_ctx_stack` 获得的

* `request` 指向是当前请求 `flask.wrappers.Request` 对象

* `session` 指向是当前的 session, `flask.sessions.SecureCookieSession` 对象

```python
# 这两个都是代理对象, 经过 RequestContext 中取得其内部的值
request = LocalProxy(partial(_lookup_req_object, 'request'))
session = LocalProxy(partial(_lookup_req_object, 'session'))
```

在 `_lookup_xx_object` 中都是调用对应的 `_ctx_xx_stack.top`, 这里检查了 `top` 是否存在, 不存在的话抛出 `RuntimeError`

```python
class LocalProxy(object):
    """代理类的源码, 主要是 __getattr__, __getitem__, __setitem__ 这些对应到内部的
       真正的对象
    """
    __slots__ = ('__local', '__dict__', '__name__', '__wrapped__')
    
    # self.__local 便是我们传入的查找函数
    def __init__(self, local, name=None):
        object.__setattr__(self, '_LocalProxy__local', local)
        object.__setattr__(self, '__name__', name)
        if callable(local) and not hasattr(local, '__release_local__'):
            object.__setattr__(self, '__wrapped__', local)
            
	def _get_current_object(self):
        # 返回了对应的 _lookup_*_object, 也就是对应的 RequestContext, 或 AppContext
        if not hasattr(self.__local, '__release_local__'):
            return self.__local()
        try:
            return getattr(self.__local, self.__name)
        except AttributeError:
            raise RuntimeError('no object bound to %s' % self.__name)
            
	# 我们在使用 request.args 这样的方法时, 其实就是 
    # RequestContext['request'][name]
    # 这样就回到了 _request_ctx_stack.request[name] 了
	def __getattr__(self, name):
        if name == '__members__':
            return dir(self._get_current_object())
        return getattr(self._get_current_object(), name)
    
    def __setitem__(self, key, value):
        self._get_current_object()[key] = value
```

所以这也说明了为什么当 outside context, `current_app`, `request`, `session`, `g` 这些代理都是不可用的, 这些代理都是去 `_request_ctx_stack` 或 `_app_ctx_stack` 查找对应的值. 当我们使用 `with flaks_app.app_context()` 的时候, 会帮我们压入一个 `AppContext` 来使用, 并帮我们管理上下文. 



















