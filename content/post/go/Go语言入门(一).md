---

title: "Go 语言入门(一)"
date: 2020-08-10
tags: ["入门", "go"]
categories: ['Go']
typora-root-url: ../../../static
draft: true

---

## 1. 程序结构

### 1.1 关键字, 内建常量, 类型及函数, 变量名称

```text
// go 里的关键字, 不能用于自定义变量名
break    	default        	func    	interface    select
case     	defer      		go      	map          struct
chan     	else       		goto    	package      switch
const    	fallthrough     if			range		 type
continue	for 			import      return       var

// 内建预定义名字, 可以重新使用
内建常量: true false iota nil

内建类型: int int8 int16 int32 int64
         uint uint8 unint16 uint32 uint64 uintptr
         float32 float64 complex128 complex64
         bool byte rune string error
         
 内建函数: make len cap new append copy close delete
          complex real image
          panic recover
```

> Go 变量名区分大小写, 但首字母大小写有特殊的意义, 用于表示是否可导出的
>
> 一般使用**驼峰式**

### 1.2 变量声明, 指针, 变量作用域及生命周期

```go
// 1. var 名称 类型
var s string
// 2. 由值自动推断类型
var s = "abc"
// 3. 简短声明 名称 := 值
s := "abc"
// 多个声明
var s1, s2, s3 string
// 元组方式赋值
var x, y = 1, 2
// 变量交换
x, y = y, x
// 正确, out 还没声明过
in, err := os.Open(infile)
out, err := osCreate(outfile)

// 错误
in, err := os.Open(infile)
in, err := osCreate(outfile)

// 改成
in, err = os.Create(outfile)

// 使用 & 获取指针
var x = 1
var y = &x
// 使用 new 函数获取指针
var m = new(int)
// 判空
z != nil
// 使用 * 获取指向的值
m := *z
```

>  1. 指针不支持运算(`++`, `--`)
>  2. Go 有块作用域, 花括号 `{}` 内的局部变量, 在外不可访问
>  3. 函数内的局部指针变量在变量返回后不会被回收
>  4. 简短式声明只能在函数内部写, 变量只能声明一次

### 1.3  运算操作符

Go 除了一些和其他语言常见的操作运算符外, 有几个运算符是比较特殊的

* `&^` 这个是位清空, `x&^y` 相当于把 `x` 上的第 `y` 位(从右开始)上置为 0, 相当 `01001100 & 11111011` 把第 3 位置为 0
* 自增 `++`, 自减 `—` 不会返回值, `x = y++` 是错误的, 并且只有后缀没有前缀 

## 2. 数据类型

### 2.1 整型

* `int8`, `int16`, `int32`, `int64` 分别对应 8, 16, 32, 64 位大小的**有符号整型**
* `uint8`, `uint16`, `uint32`, `uint64` 分别对应 8, 16, 32, 64 位大小的**无符号整型**
* `int`, `uint` 通用的**有符号**, **无符号**的整型, 根据运行的平台为 32bit 或 64bit
* Unicode 的 `rune` 类型, 等价于 `int32`, 表示 **Unicode 码点**
* `byte` 类型, 等价于 `uint8` 类型
* 无符号整数类型 `uintptr`, 没有指定具体的 bit 大小但是足以容纳指针

### 2.2. 浮点数

* `float32`, `float64` 分别对应 32, 64 位大小的**有符号浮点数**

### 2.3 复数

* `complex64`, `complex128` 分别对应 float32, float64 的浮点数精度
* 内置的 `complex` 函数构建复数, `real`, `imag` 分别返回复数的**实部**和**虚部**

```go
var x complex128 = complex(1, 2) // 1+2i
```

### 2.4 布尔型

* 只有两种 `true` 和 `false`

* 布尔值不会隐式的转换为数值 0 或 1

### 2.5 字符串

字符串是一个不可改变的字节序列, 文本字符串通常被解释为采用 UTF8 编码的 Unicode 码点 (rune) 序列

* `len` 函数可以返回的是一个字符串的**字节数目**(不是 run 字符数目), s[i] 返回的是 byte 类型
* 



















* 类型强制转换

```go
f := 3.1415
x := int(f)
```

* 不同的类型不能对比, 即使是类型别名也需要强制转换后才能对比

