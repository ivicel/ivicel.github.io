---
title: "Python super函数解析"
date: 2020-09-11
tags: ["super", "python"]
categories: ['Python']
---

## super 的说明

> Return a proxy object that delegates method calls to a parent or sibling class of *type*. This is useful for accessing inherited methods that have been overridden in a class.

这里说明 `super` 函数返回一个代理对象, 可调父类或者兄弟类中的方法, 用来调用的是被覆写方法(虽然也可以调用毫无关系的类, 但没这必要)

使用方法 `super([type[, object-or-type]])`

`super` 查找顺序是按某个类的 mro 链表中的某个结点的下一结点

这里有两个关键点, 1: 哪个类的 mro, 2: 从哪个结点的下一结点

这两个关键点就是 super 方法的两个参数, 这两个参数都非必须参数

第一个 type 就是哪个结点, 也就是位置, 第二个参数指的是哪条链

## 1. 在类中, 省略两个参数, 此时相当 super(cls, self)

```python
class A1:
    def spam(self):
        print("当前类 A1, 当前对象:", self, ", 类 A1 本身的 mro:", A1.__mro__)
        # 相当 super(A1, self)
        super().spam()


class B1:
    def spam(self):
        print("当前类 B1, 当前对象:", self, ", 类 B1 本身的 mro:", B1.__mro__)

class C1(A1, B1):
    pass

c1 = C1()
c1.spam()
```

上面的是正常调用, 这里你会发现类 `A1` 并没有继承关系, 当我们调用 `super().spam` 里, 其实是在调用 `C1.__mro__` 链中 `A1` 的下一个位置, 也就是 `B1`

> 注意 A1 此时的实例对象是 c1, 也就是子类实例对象, 这里是类的多态

```text
C1 的 mro: (<class '__main__.C1'>, <class '__main__.A1'>, <class '__main__.B1'>, <class 'object'>)
当前类 A1, 当前对象: <__main__.C1 object at 0x103bc19a0> , 类 A1 本身的 mro: (<class '__main__.A1'>, <class 'object'>)
当前类 B1, 当前对象: <__main__.C1 object at 0x103bc19a0> , 类 B1 本身的 mro: (<class '__main__.B1'>, <class 'object'>)
```

而如果我们直接调用 A1 的实例对象, 则会出错

```text
a1 = A1()
a1.spam()

出现错误:
当前类 A1, 当前对象: <__main__.A1 object at 0x10cb6f9a0> , 类 A1 本身的 mro: (<class '__main__.A1'>, <class 'object'>)
Traceback (most recent call last):
  File "test.py", line 96, in <module>
    a1.spam()
  File "test.py", line 81, in spam
    super(A1, self).spam()
AttributeError: 'super' object has no attribute 'spam'
```


## 2. 两个参数都传入

### 2.1 第二个可以传入一个对象实例 obj, `super(cls, obj)` 中此时 `isinstace(obj, cls)` 必须返回 `True`

```python
class A21:
    def p(self):
        print("当前类 A21, 当前对象:", self, ", 类 A21 本身的 mro:", A21.__mro__)

class A22:
    def p(self):
        print("当前类 A22, 当前对象:", self, ", 类 A22 本身的 mro:", A21.__mro__)

class B2(A21, A22):
    def p(self):
        print("当前类 B2, 当前对象:", self, ", 类 B2 本身的 mro:", B2.__mro__)
        b = B2()
        # 在这里我们传入的是 B2 的实例, 那应该查找, B2.mro
        # 我们也可以这样调用 A22.p 方法
        # super(A21, b).p()
        super(B2, b).p()

class C2(A21):
    def p(self):
        print("当前类 C2, 当前对象:", self, ", 类 C2 本身的 mro:", C2.__mro__)


class D2(B2, C2):
    pass


print("D2 的 mro:", D2.__mro__)
print("B2 的 mro:", B2.__mro__)
d2 = D2()
d2.p()
```

输出

```text
D2 的 mro: (<class '__main__.D2'>, <class '__main__.B2'>, <class '__main__.C2'>, <class '__main__.A21'>, <class '__main__.A22'>, <class 'object'>)
B2 的 mro: (<class '__main__.B2'>, <class '__main__.A21'>, <class '__main__.A22'>, <class 'object'>)
当前类 B2, 当前对象: <__main__.D2 object at 0x1022729a0> , 类 B2 本身的 mro: (<class '__main__.B2'>, <class '__main__.A21'>, <class '__main__.A22'>, <class 'object'>)
当前类 A21, 当前对象: <__main__.B2 object at 0x1022ca190> , 类 A21 本身的 mro: (<class '__main__.A21'>, <class 'object'>)
```

### 2.2 第二个参数也可以传入一个 type, 即 `super(type, type2)`, 但 `issubclass(type2, type)` 要返回 `True`

此时 super 返回的是一个 unbound 对象

```python
class A3:
    @classmethod
    def p(cls):
        print("在类 A3.p(cls)")

    """如果我们这样定义 p 为成员方法, 那就会出错
    def p(self):
        print('在类 A3.p(self):', self)
    """
    

class B3(A3):
    def p(self):
        print("当前类 B3, 当前对象:", self, ", 类 B3 本身的 mro:", B3.__mro__)
        # 注意这里调用的类 A3 的类方法 p
        super(B3, B3).p()

class C3(B3):
    def p(self):
        print("当前类 C3, 当前对象:", self, ", 类 C3 本身的 mro:", C3.__mro__)
        super().p()


print("C3 的 mro:", C3.__mro__)
c3 = C3()
c3.p()
```

输出

```text
C3 的 mro: (<class '__main__.C3'>, <class '__main__.B3'>, <class '__main__.A3'>, <class 'object'>)
当前类 C3, 当前对象: <__main__.C3 object at 0x10a3a3af0> , 类 C3 本身的 mro: (<class '__main__.C3'>, <class '__main__.B3'>, <class '__main__.A3'>, <class 'object'>)
当前类 B3, 当前对象: <__main__.C3 object at 0x10a3a3af0> , 类 B3 本身的 mro: (<class '__main__.B3'>, <class '__main__.A3'>, <class 'object'>)
在类 A3.p(cls)
```

## 3. 调用子类 `C1` 的对象方法, 省略第二个参数不传

当省略第二个参数不传时, 返回的也是一个 unbound 对象

但很容易让人误以为: super(A) 是 super(A, A) 的简化写法

因为 super(A, A) 也返回 unbound 方法, 代理对象是 A.mro 中 A 的下一个

可是 super(A) 并不是, 它返回的另一个代理对象, 这种用法几乎很少或者没有使用, 因为容易使人出错


```python
class B:
    a = 1

class C(B):
    pass

class D(C):
    sup = super(C)
    # pass

d = D()
# 这里就会返回 1
# 但是你不能直接这样调用 D.sup.a, 会返回找不到 attribute 'a' 错误
# d.sup.a 其实是 super(C).__get__(d, D).a 的简化

print(d.sup.a)
print(super(C).__get__(d, D).a)
```

> 说明: 这种方法很难用, 令人困惑, 几乎没人使用


## Reference

> super 完全解析说明, 虽然使用的 py2, 但讲的很清楚了
1. https://www.artima.com/weblogs/viewpost.jsp?thread=236275
2. https://www.artima.com/weblogs/viewpost.jsp?thread=236278
3. https://www.artima.com/weblogs/viewpost.jsp?thread=237121

