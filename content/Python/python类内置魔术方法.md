title: Python类内置魔术方法
date: 2017-03-20

### 内置类特殊属性

```python
object.__dict__

instance.__class__

class.__bases__

definition.__name__

definition.__qualname__

class.__mro__

class.mro()

class.__subclasses__()

```

自定义类都有一个`namespace`，即一个字典对象来存储类的属性。`C.x`即表示`C.__dict__['x']`，当类`C`中不存在属性`x`，会依据继承顺序[`MRO`](https://www.python.org/download/releases/2.3/mro/)表来查找该属性。

如若查找完基类后，依然找不到属性，才会调相应用`C.__getattribute__()`、`C.__getattr__()`

```python
class A(object):
    def __getattr__(self, name):
        print('call __getattr__()')

a = A()
a.x = 'X'
print(a.x)              # 'X', __getattr__()并未调用
print(a.__dict__)       # {'x': 'X'}

######################################

class A(object):
    x = 'A'

class B(A):
    def __getattr__(self, name):
        print('call __getattr__()')
        return 'B'

a = B() 
print(a.x)          # 'A', a.__getattr__()并不会调用

```

### `__slots__` 的特殊性
> 类变量`__slots__` 可赋值 string, iterable，字符list
> 
> 定义`__slots__`变量后，类将不再使用`__dict__`来存储属性
> 
> 类不会自动生成`__dict__`和`__weakref__`
>
>
>

### 对象方法
类中的对象方法(instance method\bound method), 其方法名也存在`M.__dict__`中，对象方法有两个只读变量`mehtod.__self__`和`method.__func__`，当调用方法时`method(arg1, arg2)`时，等于调用`method.__func__(method.__self__, arg1, arg2)`

```python
class A(object):
    def m(self):
        print('call method m')
        
a = A()
a.m()   # a.m.__func__(a.m.__self__)
```

### 访问控制 `self.x`

```python
__getattr__(self, name)

__getattribute__(self, name)

# Attribute assignments and deletions update the instance’s dictionary, never a class’s dictionary.
# If the class has a __setattr__() or __delattr__() method, 
# this is called instead of updating the instance dictionary directly.
# 删除对象的属性或者对对象属性赋值，是直接对实例 __dict__ 的操作
# 当定义了 __setattr__ 、__delattr__ 方法时，使用方法替代
__setattr__(self, name, value)

__delattr__(self, name)

```

基类 `object` 中并没有 `__getattr__()` 方法，所以，只有当自定义类的自定义了`__getattr__()`方法，才有可能访问该方法

访问属性`self.x`时，首先会隐式调用`__getattribute__()`方法，只有在`__getattribute__()`中显示调用或者`raise`出`AttributeError`时，才会调用`__getattr__()`

> 1. 类中没有定义`__getattribute__()`时，当`self.x`不存在时，默认`raise`出`AttributeError`
 
> 2. 类中有定义`__getattribute__()`时，访问`self.x`时，调用`__getattribute__()`，除非显示调用`__getattr__()`或者`raise`出`AttributeError`,才会调用`__getattr__()`如若存在
> 3. 在定义`__getattribute__()`时，为避免无限递归调用，一般使用`object.__getattribute__(self, name)`来获取对象的值


```python
class A(object):
    def __getattr__(self, name):
        print('get => ' + name)

    def __getattribute__(self, name):
        print('get attribute => ' + name)
        raise AttributeError()  # 隐式调用 __getattr__()



# get attribute => b
# get => b
# None
a = A()
print(a.b)

########################################

class A(object):
    def __getattr__(self, name):
        print('get => ' + name)

# get => b
# None
a = A()
print(a.b)

########################################

class A(object):
    def __getattribute__(self, name):
        print('get attribute => ' + name)


# get attribute => b
# None
a = A()
print(a.b)

```

### 自定义序列 self[x]

```python
__len__(self)                       # len() 方法

__getitem__(self, key)              # self[key]

__setitem__(self, key)              # self[key] = XXX

__iter__(self, key)                 # 迭代器

__reversed__(self)                  # reversed() 方法

__contains__(self, item)            # in 和 not in 测试

__missing__(self, key)              # self[key] 不存在时
```

当类没有定义`__getitem__()`时，`self['x']`会产生**`Type Error`:object is not subscriptable**, 定义`__getitem__()`后，类变成一个**subscriptor**，`self['x']`隐式调用`__getitem__()`。一般在普通的如`list`中，`x`不存在或错误会产生`KeyError`，超出范围则产生`IndexError`


### 描述符对象

```python
__get__(self, instance, owner)

__set__(self, instance, owner)

__delete__(self, instance, owner)

# 生成描述符实例时调用
__set_name__(self, owner, name)
```

> 当一个类实现`__get__()` `__set__()` `__delete__()`中一个方法，称为**描述符类**(`decriptor class`)

定义 `__set__()` and/or `__delete__()`，称为**数据描述符**(`data descriptor`); 没有定义其中一个的称为**非数据描述符**(`non-data descriptor`)

通常`data descriptor`都定义`__set__()`和`__get__()`，`non-data descriptor`只定义`__get__()`

> The following methods only apply when an instance of the class containing the method (a so-called descriptor class) appears in an owner class (the descriptor must be in either the owner’s class dictionary or in the class dictionary for one of its parents). In the examples below, “the attribute” refers to the attribute whose name is the key of the property in the owner class’ `__dict__`.
> 
> 只有描述符类的实例`instance`是`owner_class`中或`owner_class`的某一个父类中`__dict__`中属性的实例，描述符方法才会调用

描述符调用`a.x`和`A.x`

1. 直接调用`x.__get__(a)`
2. 实例对象绑定：`a.x`即`type(a).__dict__['x'].__get__(a, type(a))`
3. 类绑定：`A.x`即`A.__dict__['x'].__get__(None, A)`
4. Super绑定(继承的类有类属性是描述符的实例对象)：`super(B, obj).m`查找`obj.__class__.__mro__`，当找到`A`类有`m`属性为描述符对象时调用`A.__dict__['m'].__get__(obj, obj.__class__)`


```python
# example
# owner的类属性是一个decriptor的实例
class A(object):
    def __get__(self, instance, cls):
        print('call A.__get__()')
        return 'Class A'
        
class B(object):
    x = A()

# call A.__get__()
# 'Class A' 
b = B()
print(b.x)  

##############################

# owner的父类的属性是一个decriptor的实例
class A(object):
    def __get__(self, instance, cls):
        print('call A.__get__()')
        return 'Class A'
        
class B(object):
    x = A()
    
class C(B):
    pass
    
# print('call A.__get__()')
# 'Class A'
c = C()
print(c.x)

```

#### 对象属性访问原理
* 访问顺序：

> 资料描述器(`data descriptor`)优先于实例变量(`instance.attribute`)，实例变量优先于非资料描述器(`non-data descriptor`)，`__getattr__()`方法(如果对象中包含的话) 具有最低的优先级

```python
class descriptor(object):
    def __get__(self, instance, cls):
        print('__get__()')
        
    def __set__(self, instance, value):
        print('__set__()')
        
class A(object):
    x = descriptor()
    def __init__(self):
        # 资料描述符优先实例变量
        self.x = 'x'        #=> type(a).__dict__['x'].__set__(a, type(a))


# '__set__()'
# '__get__()'
# '__set__()'       
a = A()
a.x         #=> type(a).__dict__['x'].__get__(a, type(a))
a.x = 5     #=> type(a).__dict__['x'].__set__(a, type(a))

##############################################

class descriptor(object):
    def __get__(self, instance, cls):
        print('__get__()')
        
class A(object):
    x = descriptor()
    def __init__(self):
        # 实例变量优先非资料描述符
        self.x = 'x'        #=> self.__dict__['x'] = 'x'


# x
# {'x': 'x'}        
a = A()
print(a.x)          
print(a.__dict__)       

##############################################

class descriptor(object):
    def __get__(self, instance, cls):
        print('__get__()')
        
class A(object):
    x = descriptor()

    def __getattr__(self, key):
        print('__getattr__()')

# '__get__()'   
a = A()
# 非资料描述符优先 __getattr__ 
a.x         #=> type(a).__dict__['x'].__get__(a, type(a))

```



#### 描述符(descriptor)举例

> 内置 property 的实现

```python
class Property(object):
    def __init__(self, func):
        self._func_getter = func

    def __get__(self, instance, cls):
        return self._func_getter(instance)

    def __set__(self, instance, value):
        if getattr(self, '_setter', False):
            self._func_setter(instance, value)
        else:
            raise AttributeError("can't set attribute")

    def setter(self, func):
        self._setter = True
        self._func_setter = func
        return self

class A(object):
    @Property
    def say_hello(self):
        if hasattr(self, '_x'):
            return self._x
        else:
            return 'xxxxxxxxxxxxx'

    @say_hello.setter
    def say_hello(self, value):
        print('say hello again')
        self._x = value
```

> `classmethod`和`staticmethod`的简单实现

```python
class ClassMethod(object):
    def __init__(self, func):
        self._f = func
        
    def __get__(self, instance, cls):
        def func():
            return self._f(cls)
        return func
        
class StaticMethod(object):
    def __init__(self, f):
        self._f = f
        
    def __get__(self, instance, cls):
        return self._f

```

-------------------

### 比较操作符

```Python
__eq__(self, other)     # ==

__ne__(self, other)     # !=

__lt__(self, other)     # <

__gt__(self, other)     # >
    
__le__(self, other)     # <=

__ge__(self, other)     # >=

```

### 数值操作符

.1 一元操作符

```python
__post__(self)          # 取正 +some_object

__neg__(self)           # 取负 -some_object
    
__abs__(self)           # 绝对值 abs()

__invert__(self)        # 取反 ~

__round__(self, n)      # 内建函数 round()

__floor__(self)         # math.floor() 函数，向下取整

__ceil__(self)          # math.ceil() 函数，向上取整

__trunc__(self)         # math.trunc() 函数，距离0最返的整数

```

.2 算数操作符

```python
__add__(self, other)

__sub__(self, other)

__mul__(self, other)

__floordiv__(self, other)

__truediv__(self, other)

__mod__(self, other)

__divmod__(self, other)

__pow__(self)

__lshift__(self, other)

__rshift__(self, other)

__and__(self, other)

__or__(self, other)

__xor__(self, other)

```

.3 反射算数运算符

```python
__radd__(self, o)

__rsub__(self, o)

__rmul__(self, o)

__rfloordiv__(self, o)

__rtruediv__(self, o)

__rmod__(self, o)

__rpow__(self)

__rlshift__(self, o)

__rshift__(self, o)

_rand__(self, o)

__ror__(self, o)

__rxor__(self, o)

```

.4 增强赋值运算符

```python
__iadd__(self, o)

__isub__(self, o)

__imul__(self, o)

__ifloordiv__(self, o)

__itruediv__(self, o)

__imod__(self, o)

__ipow__(self, o)

__ilshift__(self, o)

__irshift__(self, o)

__iand__(self, o)

__ixor__(self, o)

```

.5 类型转换操作符

```python
__int__(self)

__long__(self)

__float__(self)

__complex__(self)

__oct__(self)

__hex__(self)

__index__(self)

__trunc__(self)

```

### 类的表示

```python
__str__(self)

__repr__(self)

__format__(self)

__hash__(self)

__dir__(self)

```

### 反射

```python
# isinstance(instance, class) 方法
__instancecheck__(self, instance)       

# issubclass(subclass, class) 方法
__subclasscheck__(self, subclass)       
```

### 抽象基类

```python 

```

### 可调用的对象

```python
__call__(self, [args...])

class A():
    def __call__(self):
        pass
        
a = A()
a()     # 调用A.__call__()
```

### 上下文管理器

```python
# 使用 with 声明时调用，返回值即为 as 后的东西
__enter__(self)

# 退出 with 时调用，处理 with 产生的 exception
__exit__(self, exceptiop_type, exception_value, traceback)
```

### 拷贝

```python
__copy__(self)

__deepcopy__(self, memodict=)
```