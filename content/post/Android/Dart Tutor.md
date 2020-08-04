---

title: "Dart Tutor"
date: 2019-07-01
tags: ["dart"]
categories: ['Android']

---

### 一个基本的 Dart 程序

```dart
printInteger(int aNumber) {
  print('The number is $aNumber.')
}

// 程序入口
main() {
  var number = 42;
  printInteger(number);
}
```

### 一些重要的概念

* 在 Dart 中, 所有的一切都是对象, 继承自 `Object` 类, `null` 类型也是一个对象
* Dart 是强类型语言, 但变量的声明是可以省略类型的, 程序会在第一次赋值时自动推断类型. 也可以使用 `dynamic` 关键字来声明动态类型
* Dart 支持泛型, 如 `List<int>` 或 `List<dynamic>`
* Dart 支持 top-level 函数(C 语言中的函数定义), 类成员方法, 静态方法, 也同样支持在函数中再定义函数
* Dart 支持 top-level 变量, 类成员变量, 静态变量
* Dart 没有 `pulibc`, `private`, `protected` 关键字, 使用前置下划线 `_` 来表示变量只能 library 访问
* *Identifiers* 可以以下划线 `_` 或大小写字母开始, 可以包含数字
* Dart 编译工具编译时会产生: `warnings` 和 `errors`, warning 只能产生警告而不会中止程序运行. errors 可能会在编译时或运行产生, 程序不会继续运行, 并产生 exception

### Keywords

|关键字       |           |              |          |
| ---------- | --------- | ------------ | -------- |
| `abstract` | `dynamic` | `implements` | `show`   |
| `as`       | `else`    | `import`     | `static` |
| `assert` | `enum` | `in` | `super` |
| `async` | `export` | `interface` | `switch` |
| `await` | `extends` | `is` | `sync` |
| `break` | `external` | `library` | `this` |
| `case` | `factory` | `mixin` | `throw` |
| `catch` | `false` | `new` | `true` |
| `class` | `final` | `null` | `try` |
|`const`|`finally`|`on`|`typedef`|
|`continue`|`for`|`operator`|`var`|
|`convariant`|`Function`|`part`|`void`|
|`default`|`get`|`rethrow`|`while`|
|`deferred`|`hide`|`return`|`with`|
|`do`|`if`|`set`|`yield`|

### 变量

Dart 可以使用 `var` 关键字来定义变量, 如 `var name = 'Bob'`, Dart 会自动推断会变量的类型, Dart 也可以显示的设置变量类型 `String name = 'Bob'`, 设置一但设置便不能更改, 若要使用动态类型, 可以使用 `dynamic` 类型

#### 默认值

未初始化的变量是默认值为 `null`, 即使其类型为 `int`

#### Final 和 const 修饰

`final` 关键字表示变量在定义之后再无法修改, 其值在运行时确定

`const` 关键字表示变量的值在编译(**compile-time constants**)时就已经确定, 并且无法更改, 也就是

```dart
final name = 'Bob';    // name 无法再重新赋值

const age = 12;        // 正确, 12 是一个确定的值

int get(int i) {
  return i * i;
}
const j = get(2);      // 错误, j 的值要到运行时才能确定
```

### Built-in types

* numbers
* strings
* booleans
* lists ( 列表或数组)
* sets
* maps
* runes (Unicode 字符)
* symbols

#### Numbers

Dart 数值在 `int` 和 `double` 两种类型. `int` 最大为 64 bits, double 为双精度 64 bits

`int` 和 `double` 都是 `num` 的子类型, 可以使用 `num i = 3` 来定义变量数值

#### Strings

字符串可以使用单引号 `'` 或双引号 `"` 来定义, 引号内可以使用 `$` 来引用变量的值, 和 java 不同的是, 字符串值使用 `==` 比较

```dart
var s = 'word';
var str = 'Hello, $s';
print(str);     // Hello, word
```

另外, dart 中还支持和 python 中一样的多行字符, `'''` 和 `"""`, 原始字符 `r`

```dart
var s` = '''
You can create
multi-line strings like this one.
''';

var s2 = """This is also a
multi-line string.""";

// 使用 r 标志, \n 不会被转义为换行
var s = r'abc,\n gets special';
```

#### Booleans

只有 `true` 和 `false` 两个值, 在 dart 中 if 判断只能是这两个值, 不会自动推断, 和 java 是一样的. `if (a == null)`

#### List

列表或者数组, `var list = [1, 2, 3, 4];` list 类型为 `List<int>`. 在 dart 2.3 添加了 **spread operator**(`…`) 和 **null-aware spread operator**(`…?`) 用来添加列表

```dart
var list = [1, 2, 3];
var list2 = [0, ...list];    // [0, 1, 2, 3, 4]

var l1;
var l2 = [0, ...?l1];    // [0], ...? 用来判断 null 值

// collection if 语句
var nav = [
  'Home',
  'Furniture',
  'Plants',
  if (promoActive) 'Outlet'
];

// collection for 语句
var listOfInts = [1, 2, 3];
var listOfStrings = [
  '#0',
  for (var i in listOfInts) '#$i'
];
```

#### Sets

无序不重复的集合.

```dart
// 字面量定义, 使用 {} 定义
var halogens = {'fluorine', 'bromine'};

// {} 指的是空 map, 当要定义空 set 时, 使用 Set 类
var s = <String>{};
```

#### Map

```dart
var gifts = {
  'first': 'partridge',
  'second': 'turtledoves',
  'fifth': 'golden rings'
};

// dart 2 中 new 关键字可以省略
var gift2 = Map();
gift2['first'] = 'partridge';
```

#### Runes

在 dart 中, runes 是 UTF-32 code points 字符串.

```dart
Runes input = Runes('\u2665 \u{1f605}');
```

#### Symbols

`Symbols` 对象代表的是一个操作符或标识符, 比如 `#radix`, 可用于类似 C 中的 goto 跳转

### Functions

Dart 是一个纯面向对象语言, 函数也是一个对象, 所以可以将函数当作一个参数传递给另一个函数. 函数如果没有写返回值, 则默认返回 `null`

```dart
// number 的类型和返回值都可以省略, 但为代码阅读方便, 最好不要省略
bool isNoble(int number) {
  return _nobleGases[number] != null;
}

// return 可以简写成 =>, 但和 javascript 的 => 函数不同
// 这里只是一个语法糖, => 后面只能是一条表达式, 不能有多条
bool isNoble(int number) => _nobleGases[number] != null;
```

#### 可选参数和默认参数值

有两种方法表示可选参数, 命名参数(Optional named parameters), 使用 `{...}`,  位置参数(Optional positional parameters), 使用 `[…]`, 两种方式不能混合使用. 另外在可选参数中还可以使用 `@required` 标识注明该参数必须传值. 默认的参数值只能是使用在可选参数中设置

```dart
// 命名参数, 定义时使用 {paramType paramName}
void namedParamFunc({bool bold, bool hidden}) {...}
// 调用时 paramName: value
namedParamFunc(bold: true, hidden: false);

// 也可以使用 @required 表明该参数 hidden 必须传一个值
void namedParamWithRequired({bool bold, @required bool hidden) {...}

// 位置参数, 使用 [], 位置可选参数必须位于必传参数后面
void positionalParamFunc(String from, String msg, [String device]) {...}
                  
// 设置默认参数, 默认参数必须是 const
void defaultParamFunc1({bool bold = false, bool hidden}) {...}
void defaultParamFunc2(String from, String msg, [String device = 'android']) {...}
void defaultParamFunc1({bool bold = false, List<int> numbers = const [1, 2, 3}) {...}
```

#### 匿名函数

```dart
/* 
([[Type] param [, ...]]) {
  codeBlock;
};
*/

var list = ['apples', 'bananas', 'oranges'];
  list.forEach((item) {
    print('${list.indexOf(item)}: $item');
  });
```

### 几个特殊操作符

#### 级联操作符(Cascade notation ..)

类似于 java 中类返回 `this` 里可级联的操作, dart 中不必显示返回 this

```dart
querySelector('#confirm') // Get an object.
  ..text = 'Confirm' // Use its members.
  ..classes.add('important')
  ..onClick.listen((e) => window.alert('Confirmed!'));

// 相当于, 这里 querySelector 一定要返回一个对象
var button = querySelector('#confirm');
button.text = 'Confirm';
button.classes.add('important');
button.onClick.listen((e) => window.alert('Confirmed!'));
```

#### 判断 null 操作符

#### `is`, `as`, `is!`, `??`, `?.`

`is` 相当于 java 中 `instaceof`, 判断 对象是否是某个类的实例, `is!` 反之

`as` 用于类型强制转换或在 library import 中重命别名

`?.` 用于在类对象访问成员方法/成员变量, 先进行判断 `null` 操作, 以免产生错误

```dart
// 用于判断 obj 是否为 null, 以免产生错误
var a = obj?.a;
```

`??` 用于判断是是否为 `null`

```dart
// 如果 b 为 null, a 保持不变, 否则则把 b 的值赋给 a
var a = 'abc';
a ??= b;

// 如果 name 为 null, 则返回 Guest
String playerName(String name) => name ?? 'Guest';
// 相当
String playerName(String name) => name != null ? name : 'Guest';
```

### 控制流程

`switch` 语句中, 如果  `case` 里面有写了语句, 则 `break` 不能缺少, 否则会产生错误. 另外还支持跳转到类似锚点的形式, 使用 `continue [tagPosition]` 语句

```dart
switch (c) {
  case 'OPEN':
    doA();
    // 错误, 缺少 break
  case 'CLOSED':
    doB();
    break;
}

var command = 'CLOSED';
switch (command) {
  case 'CLOSED':
    executeClosed();
    continue nowClosed;
  // Continues executing at the nowClosed label.

  nowClosed:
  case 'NOW_CLOSED':
    // Runs for both CLOSED and NOW_CLOSED.
    executeNowClosed();
    break;
}
```

### 异常 Exceptions

抛出异常 `throw FormatException('error…')`, dart 可以抛出任何非 null 对象, 如 `throw 123`. 捕获异常使用 `on` 和 `catch` 关键字

```dart
try {
  breedMoreLlamas();
} on OutOfLlamasException {
	// 捕获特定异常
} on Exception catch (e, s) {
  // 捕获特定异常, e 是异常对象, s 是栈错误对象 StackTrace, 可以省略
  print('Unknown exception: $e');
} catch (e) {
  // 捕获所有异常
} finally {
 	// 一定执行的语句 
}

```

### 类 Classes

* 类的初始化顺序: 1. 参数列表, 2. 父类 constructor, 3. 本类 constructor
* 类的成员变量默认都有 getter/setter 方法, 和 python 中一样直接赋值, 以 `_` 开始的为可在 library 内访问, 没有 private, public, protected 修饰
* 获取对象的类型可以使用 `obj.runtimeType` 成员变量

#### 构造方法

如果不声明构造方法, 则类有一个无参的默认构造方法. 构造方法是不继承的. 构造方法有两种写法, 类似 java 的, 和命名构造方法

##### 类 Java 的构造方法

```dart
class Point {
  num x, y;
  
  // 也可以简写成 Point(this.x, this.y);
  Point(num x, num y) {
    this.x = x;
    this.y = y;
  }
```

##### 命名构造方法

```dart
  // 命名构造方法
  Point.origin() {
    x = 0;
    y = 0;

// 调用
var p1 = Point(1, 2);
var p2 = Point.origin();
```

#### 使用构造方法初始化列表

```dart
// 类的初始化列表
class MyPoint {
 	num x, y;
  
  // : 后面是初始化表, 会先方法内部进行调用, 类似 C++, 也可以是其他表达式, 比如 assert(x >= 0)
  MyPoint.fromJson(Map<String, num> json):
  		x = json['x'],
  		y = json['y'] {
  	print('In MyPoint.fromJson: ($x, $y)');      
  }
}
```

#### constant 类

```dart
// Constant constructors, 其成员变量必须都是 final
class ImmutablePoint {
 	final num x, y;
  
  const ImmutablePoint(this.x, this.y);
}

// 调用
var immutablePoint = const ImmutablePoint(1, 2);
```

#### 使用 `factory` 设置工厂方法

```dart
// 工厂方法 constructor, 使用 factory 关键字, 工厂方法不能访问 this
class Logger {
  final String name;
  
  static final Map<String, Logger> _cache = <String, Logger>{};
  
  factory Logger(String name) {
    	if (_cache.containsKey(name) {
        return _cache[name];
      } else {
        final logger = Logger._internal(name);
        _cache[name] = logger;
        return logger;
      }
   }
   
	 Logger._internal(this.name);
}
```

#### 抽象类: `abstract`

```dart       
// 抽象类, 使用 abstract 关键字, 继承时必须要覆写
abstract class Dog {
  // 抽象类中不写方法体的便是抽象方法, 不用 abstract 关键字
  void doSomething();
}
```

#### `as` 向上/下转型

```dart
class Person {}
class Employee extends Person {}

var em = Employee();
(em as Person).doSomething();
```

#### 隐式接口 implicit interfaces

每一个类都是一个隐式的接口, dart 里没有像 java 的 interface 关键字, 当我们使用 `extends` 继承类时, 会继承类的实现, 而实现 `implements` 接口的话, 并不会继承原类里的实现. 可以实现多个接口. 实现接口的时候必须要实现**所有的成员变量和成员方法**

```dart
class Person {
  final _name;
  Person(this._name);
  
  String greet(String who) => 'Hello, $who. I am $_name.';
}

class Impostor implements Person {
  // 别忘实现成员变量
  String _name;
  
  // 实现成员方法
  String greet(String who) => 'Hi, $who';
}

String greetBob(Person person) => person.greet('Bob');

greetBob(Person('Kathy'));
greetBob(Impostor());
```

#### 继承及调用父类

使用 `extends` 继承类, 只能单继承. 子类构造方法会默认调用父类的**无参**, **非命名** 的构造方法, 如果不存在的话, 要手动使用 `super` 调用, 调用要放在初始化列表中, 在构造方法函数体之前.

可以使用 `@overirde` 注解标识覆写的方法.

> 构造方法不会被继承的

```dart
class A {
  final _name;
  A(this._name);
  
  void print() => print(_name);
}

class B extends A {
  B(String name) : super(name);
  
  @override
  void print() => print('hello, $_name');
}
```

#### 覆写操作符

dart 支持类似 C++ 对操作符进行覆写, 支持以下操作符, 使用 `operator` 关键字. 

* `<`, `>`, `<=`, `>=`
* `+`, `-`, `*`, `/`, `~/`, `%`, `~`, `==`
* `>>`, `<<`, `|`, `^`, `&`
* `[]`, `[]=`

> 注意 `!=` 并不支持覆写, 如要判断 `e1 != e2`, 只能取巧 `!(e1 == e2)`
>
> 如果覆写 `==` 一定要同时覆写 `hashCode` 方法

```dart
class Vector {
  final int x, y;
  
  Vector(this.x, this.y);
  
  Vector operator +(Vector v) => Vector(x + v.x, y + v.y);
  Vector operator -(Vector v) => Vector(x - v.x, y - v.y);
}
```

#### `noSuchMethod` 方法

当访问不存在的**方法或变量**时, 会调用该方法, 默认的实现抛出 `NoSuchMethodError`

```dart
class A {
  @override
  void noSuchMethod(Invocation invocation) {
    print("no such $(invocatino.memberName);");
  }
}
```

### 枚举类型 Enumerated types

```dart
enum Color { red, green, blue }
```

### mixins 类(dart 2.1 之后)

Mixins 是为了重用类, 解决单继承的另一种方式, 定义一个 mixin 类需要使用 `mixin 关键字, 使用 `with` 关键字来继承 mixin 类

```dart
// 定义 mixin 类
mixin Musical {
  bool canPlayPiano = false;
  
  void entertainMe() {
    // do something....
  }
}

// 使用 with 关键字
class Musician extends Performer with Musical {}
```

可以限制哪个类可以继承 mixin 类, 使用 `on` 关键字

```dart
mixin MusicalPerformer on Musician {
  // something...
}
```

### 泛型

* dart 里的泛型类似 java 的泛型, 如定义  `class Cache<T>`, 另外还可以限制泛型的类型 `class Cache<T extends SomeBaseClass>`

* 泛型方法, `T first<T>(List<T> ts)`

#### 参数化 collection 字面量和构造方法

```dart
var nameList = <String>['a', 'b', 'c'];
var nameSet = <String>{'a', 'b', 'c'};
var nameMap = <String, String>{
  'a': 'a',
  'b': 'b'
};

var nameSet2 = Set<String>.from[nameSet];
```

### Libraries

`import` 和 `library` 关键字用来导入和定义模块, 使用 `_` 开始的只能在模块内可见, 每一个 dart app 都是一个模块, 无论是否有用 `library` 声明

导入语句 `import 'package:test/test.dart';`

对于内置的模块, 其包名都为 `dart`, 如 `import dart:html;`

对导入的包重命别名: `import 'package:lib2/lib2.dart' as lib2;`, 使用 `as` 关键字

#### 部分导入

```dart
// 只导入 foo
import 'package:lib1/lib1.dart' show foo;
// 导入除 foo 之外
import 'package:lib2/lib2.dart' hide foo;
```

#### 懒导入(deferred loading 或 lazy loading)

> 懒导入只能在 dart2js 中使用

```dart
// 使用 deferred as 语句
import 'package:greetings/hello.dart' deferred as hello;

// 调用懒导入的库, 调用之前要先调用 loadLibrary 方法
Future greet() async {
  await hello.loadLibrary();
  hello.printGreeting();
}
```

### 异步

异步使用 `async` 和 `await`, 使用 `async` 的函数总是会返回 `Future` 对象, 不用显示的返回 `Future`, 程序会自动包装, 如果没有返回值则是 `Future<void>` 类型. `awati` 只能在 `async` 函数中使用

```dart
Future checkVersion() async {
  var version = await lookUpVersion();
  // do something
}

// 在 main 中也可以使用 async
Future main() async {
  checkVersion();
  print('.....');
}
```

### 异步流 Streams

使用 `await for` 可以获取异步循环, `await for (var id in expression)`. 可以使用 `break` 或者 `return` 中断循环. 注意 `await for` 只能在 `async` 函数中使用

### 生成器 Generators

* 同步生成器 Synchronous generator, 返回 `Iterable` 对象, 使用 `sync*` 修饰函数

```dart
Iterable<int> naturalsTo(int n) sync* {
  int k = 0;
  while (k < n) {
    yield k++;
  }
}
```

* 异步生成器 Asynchronous generator, 返回 `Stream` 对象, 使用 `async*` 修饰函数

```dart
Stream<int> asynchronousNaturalsTo(int n) async* {
  int k = 0;
  while (k < n) {
    yield k++;
  }
}
```

类似 Python 里的 yield from, 使用 `yield*` 在生成器中返回生成器

```dart
Iterable<int> naturalsDownFrom(int n) sync* {
  if (n > 0) {
    yield n;
    yield* naturalsDownFrom(n - 1);
  }
}
```

### 可调用的类对象 Callable classes

类似 Python 类对象可调用的魔术方法 `__call__`, dart 里也有一个类内置的方法 `call()`, 实现这个方法类对象便也可以像函数一样调用

```dart
class WannableFunction {
  call(String a, String b, String c) => '$a, $b, $c';
}

var wf = WannableFunction();
print(wf('Hi', 'there', 'gang'));
```

### Typedefs

类似 C 中的 typedef, 定义类型别名, typedefs 让我们能保持类型的信息, 比如

```dart
class SortedCollection {
  Function compare;
  
  SortedCollection(int f(Ojbect a, Object b)) {
    compare = f;
  }
}
```

原先 `f` 是一个接受两个参数并返回 `int` 的函数, 但传给 `compare` 之后, 便只能得到一个 `Function` 类型, 已经没有参数和返回值的信息, 使用 `typedef` 可以解决这问题

```dart
typedef Compare = int Function(Object a, Object b);

class SortedCollection {
  Compare compare;
  
  SortedCollection(this.compare);
}

// 也可以使用泛型
typedef Compare<T> = int Function(T a, T b);
```



