---

title: "python tips"
date: 2018-09-10
tags: ["tips"]
categories: ['Python']
header-image: "hello fjdalksfj.jpg"

---

```python
a = (1, 2, [3, 4])
a[2] += [5, 6]

# 以上在 python 3.6.5 中抛出了 TypeError, 但 a[2] 的值还是变成了 [3, 4, 5, 6]
# 这是因为 a[2] 在增量时是分成两步
# 一是把 a[2] 的列表值入栈, 扩展成 [3, 4, 5, 6], 这是成功的
# 二是赋值回给元组元素 a[2], 这一步就出现的 TypeError
```

* 不要把可变对象放在元组中
* 列表增量赋值不是一个原子, 是分成两步进行的, 其实也可以从 list 没有实现 `__iadd__()` 可以看出. 因为自增会调用该方法, 如果没有实现该方法, 便才会调用 `__add__()` , 然后把结果赋值给原对象
* 可以通过 `dis.dis` 来查看 python 的字节码





#### Python 代码会在何时运行

##### 1. 代码作用模块导入时

> 代码是从上到下运行

* **各种 `import` 语句**

  一般我们会把各种 `import` 写在前面时, 会运行 `import` 各种模块, 这个和 `Java` 是不一样的, `Java` 的 `import` 只是一种声明并不运行.

* **全局各种语句**

  比如 `n = 3`, `print('hello, world)` 之类写在非函数, 类内的

* **类定义体**

  比如属性的初始化, **写在非方法内的语句都会初始化运行**, 如果类内还有嵌套类, 嵌套类的定义体也会运行. 比如有下面类的定义

```python
# print('initial A...'), print('initial B...') 语句 和 m = 3 会被运行

class A(object):
    m = 3
    print('initial A...')
    
    def __init__(self, a):
        self.a = a
        
    class B(object):
        print('initial B...')
```

* **类的元类**
  类的元类会被调用来初始化类, 比如

  ```python
  # 作为 B 的元类, A.__new__, A.__init__ 都会被调用
  class A(type):
      def __new__(meta, name, bases, attrs):
          # meta 是传入的元类, 也就是类 A 本身
          # name 是要初始化类的名称, 也就是字符 'B'
          # bases 是类 B 的基类, tuple 类型
          # attrs 是类 B 的属性, 包括方法和类属性
          # 最终交给 type 来初始化, 避免无限循环, 元类主要是中间拦截
          print('A.__new__()')
          return type.__new__(meta, name, bases, attrs)
  	def __init__(cls, name, bases, attrs):
          # type.__new__ 会调用这个方法
          # cls 是生成的类
          print('A.__init__()')
          
  class B(metaclass=A):
      def __init__
  ```

  > 只有继承了 **type** 的才能作为**元类**, 元类的 `__new__`, `__init__` 参数是固定的 

* **装饰器**

  装饰器会被动行, 装饰器的运行顺序比如. 
  
  ```python
  # 装饰器相当于 ClassThree = deco_alpha(ClassThree) 
  # 所以是先被装饰者运行, 然后才到装饰器本身
  @deco_alpha
  class ClassThree():
  	def m(self):
  		pass
  ```
  

##### 2. 从命令行中运行

跟导入时相同, 但会执行 `__name__ == '__main__':` 中的语句


