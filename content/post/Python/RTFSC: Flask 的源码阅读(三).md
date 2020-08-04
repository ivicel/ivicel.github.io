---

title: "RTFSC: Flask 的源码阅读(三)"
date: 2018-09-19
tags: ["flask", "python", "源代码阅读", "RTFSC"]
categories: ['Python']

---



#### 1. 路由的实现

有两种方式来添加路由, 通常使用装饰器来添加, 其内部也是通过第二种 `add_url_rule()` 方法, 装饰器是一种简洁明了的方式. 

```python
def add_url_rule(self, rule, endpoint=None, view_func=None,
                 provide_automatic_options=None, **options):
    # endpoint 默认使用的是函数名
    if endpoint is None:
        endpoint = _endpoint_from_view_func(view_func)
    options['endpoint'] = endpoint
    # 提供 HTTP 方法
    # 1) methods 参数 2) 从 view_func 的 methods 属性 3) view_func 的 require_methods 属性
    # 如果这两个都没提供, 则默认只支持 GET
    methods = options.pop('methods', None)
    if methods is None:
        methods = getattr(view_func, 'methods', None) or ('GET',)
    if isinstance(methods, string_types):
        raise TypeError('Allowed methods have to be iterables of strings, '
                        'for example: @app.route(..., methods=["POST"])')
    methods = set(item.upper() for item in methods)

    # Methods that should always be added
    required_methods = set(getattr(view_func, 'required_methods', ()))

    # provide_automatic_options 为非 None 时不会自动提供 OPTIONS 方法
    if provide_automatic_options is None:
        provide_automatic_options = getattr(view_func,
            'provide_automatic_options', None)

    if provide_automatic_options is None:
        if 'OPTIONS' not in methods:
            provide_automatic_options = True
            required_methods.add('OPTIONS')
        else:
            provide_automatic_options = False

    # Add the required methods now.
    methods |= required_methods

    rule = self.url_rule_class(rule, methods=methods, **options)
    rule.provide_automatic_options = provide_automatic_options

    self.url_map.add(rule)
    if view_func is not None:
        old_func = self.view_functions.get(endpoint)
        if old_func is not None and old_func != view_func:
            raise AssertionError('View function mapping is overwriting an '
                                 'existing endpoint function: %s' % endpoint)
        self.view_functions[endpoint] = view_func

```

