title: C 语言简记
date: 2017-03-20
tags: C



First C program

```c
#include <stdio.h>

int main(int argc, char **argv)
{
    printf("Hello C!!!\n");
}
```

#### **1. 注释** 

```c
/* 
 *
 * 注释不能嵌套 
 *  
 */
```

#### **2. 关键字、保留字**

| `auto`    | `else`     | `long`     | `switch`  | `break`    |
| --------- | ---------- | ---------- | --------- | ---------- |
| `enum`    | `register` | `typedef`  | `case`    | `extern`   |
| `union`   | `char`     | `float`    | `short`   | `unsigned` |
| `const`   | `for`      | `signed`   | `void`    | `continue` |
| `goto`    | `sizeof`   | `volatile` | `default` | `if`       |
| `static`  | `while`    | `do`       | `struct`  | `int`      |
| `_Packed` | `double`   |            |           |            |




#### **3. 数据类型**

整型  
 - (`signed`或`unsinged`)  
 - `char`  
 - `int`   
 - `short`   
 - `long`  

浮点型  
 - `float`  
 - `double`  
 - `long double`  

数据在系统中占据的内存大小，与系统类型有关

![存储大小](../../assets/images/存储大小.jpg)

`void`类型

作为函数返回值: `void func(int status)`  
作函数参数: `int rand(void)`  
作可变指针: `void *malloc(size_t size)`


#### **4. 标识符，变量**
以`A-Z`或`a-z`或`_`开头，加上数字  
`extern`关键字声明而不定义，在别的文件定义该变量

1. 在函数或块内部的**局部变量**
2. 在所有函数外部的**全局变量**
3. 在函数中定义的**形式参数**

```c
#include <stdio.h>

/* 全局变量 */
/* 不手动初始化时，默认值被系统初始化为:
 * int => 0
 * char => '\0'
 * float => 0
 * double => 0
 * pointer => NULL
 */
int a;
int main(void)
{
    /* 局部变量 */
    int b;
    
}
/* 形式变量 */
void func(int a)
{
    /* do something */
}
```


#### **5. 常量**
整数常量：十进制、十六进制(前缀`0x`或`0X`)、八进制(前缀`0`)，可以带上后缀`U` `u`(表示`unsigned`), `L` `l`(表示`long`)  
浮点常量：`e`或`E`的指数 `1.3`  
字符常量：`'x'`, `'y'`, 转义字符  
字符串常量：`"hello"`

定义常量：

```c
/* 1. define预处理器 */ 
#define LENGTH 10
/* 2. const关键字 */
const int LEN = 10
```

#### **6. C存储类**
1. `auto`: 局部变量默认类型，只能在局部变量使用  
2. `register`: 存储在寄存器中，不能对其使用`&`运算符
3. `static`: 静态变量  
- 修饰局部变量时，变量退出函数时不会被销毁  
- 修饰全局时该变量只能在当前文件使用
4. `extern`: 全局变量在所有程序文件可见，对于无法初始化的变量，会把变量名指向一个之前定义过的存储位置。

#### **7. 运算符**
算术运算符: `+`, `-`, `*`, `/`, `%`, 前/后缀`++`, 前/后缀`--`  
关系运算符: `==`, `!=`, `>`, `<`, `>=`, `<=`  
逻辑运算符: `&&`, `||`, `!`  
位运算符: `|`, `&`, `^`, `~`(取反), `<<`(左移), `>>`(右移)  
赋值运算符: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `<<=`, `>>=`, `&=`, `|=`, `|=`  
其他运算符: `sizeof`, `&`(返回变量地址), `*`(指向一个变量), `?:`

#### **8. 语句**

```c
/* 判断 */
if (a == b) {
    printf("yes\n");
} esle {
    print("no\n");
}

if (c == d) {
    /*..*/
} else if (e == f) {
    /*..*/
}

switch (a) {
    case 0:
        /*..*/
        break;
    default:
        /*..*/
}

/* 循环 */
while (a != 0) {
    /* do something */
}

do {
    /* do something */
} while (a != 0)

for (int i = 0; i < 10; i++) {
    /* do something */
}

/* continue 语句 */
/* goto 语句 */

```

#### **9. 函数**

```c
/* 传值 */
int func1(int a, int b)
{
    /* do something */
    return a;
}

/* 引用 */
int func2(int *a, int *b)
{
    /* do something */
    return a;
}
```

#### **10. 数组**

```c
double balance[10];
int a[5] = {1, 2, 3, 4, 5};
char b[6] = "hello";    /* 最后一位存储'\0' */
int c[] = {1, 2, 3, 4}; /* 忽略数组大小时，数组大小初始化为元素个数 */
/* 多维数组 */
int val[3][2] = {
    {0, 1},
    {2, 3},
    {4, 5}
}
```

#### **11. 指针**

```c
/* 指针的大小跟系统有关，64位中为8个字节 */
int a = 5;
int *p1 = &a;    /* p是a的地址，*p是a的值 */
int *p2 = NULL;  /* 空指针 */
/* 指针运算, 其实是内存的运算，指针的类型决定其运算增加或减少几个字节 */
p++;
p--;
p1 > p2;
/* 指针数组 */
int a = 5;
int *p[3];
p[0] = &a;
/* 指向指针的指针 */
int a = 5;
int *p = &a;
int **ptr = &p;
```

#### **12. 结构体**

```c
/* 定义 */
struct Books {
    char title[50];
    int book_id;
};

/* 声明 */
struct Books b1;
struct Books *book_ptr;
/* 访问 */
b1->title;
b1->book_id;
```

#### **13. 共用体**

```c
/* 大小是占内存最大的成员的大小 */
union Data {
    int i;
    float f;
    char str[20];
}data;
/* 访问 */
data.i;
data.f;

/*********************************/
#include <stdio.h>
#include <string.h>

int main()
{
    union Data {
        int i;
        float j;
        char a[20];
    }data;

    data.i = 10;
    data.j = 2.3;
    /* 最的出赋值覆盖了前面的值 */
    strcpy(data.a, "C Programming");
    printf("data.i = %d\n", data.i);
    printf("data.j = %f\n", data.j);
    printf("data.a = %s\n", data.a);

    return 0;
}

/* 输出 */
data.i = 1917853763
data.j = 4122360580327794860452759994368.000000
data.a = C Programming

/**************************************/
#include <stdio.h>
#include <string.h>

int main()
{
    union Data {
        int i;
        float j;
        char a[20];
    } data;

    data.i = 10;
    printf("data.i = %d\n", data.i);
    data.j = 2.3;
    printf("data.j = %f\n", data.j);
    strcpy(data.a, "C Programming");
    printf("data.a = %s\n", data.a);

    return 0;
}

/* 输出正常 */
data.i = 10
data.j = 2.300000
data.a = C Programming
```

#### **14. 位域**

```c
/* 一个位域必须存储在同一字节中，有些编译器可以跨字节，可以有空域来作占位符 */
/* 因为不能跨字节，所以位域最大为8位，大于8位产生不可预计影响 */
/* 无名位域即空域，只能用来作占位符，不能被使用 */

/* 位域使用struct声明 
 * struct {
 *     type [member_name] : width;
 * };
 * type可以是有符号或无符号整型，准定了如何解释位域
 */
struct {
    /* 只占4个字节，并且只有两bit被使用 */
    unsigned int width:1;       
    unsigned int length:1;
}status;

struct {
    unsigned a:4;
    unsigned :4;    /* 空域 */
    usigned b:4;    /* 从下一个字节开始存储 */
    usigned c:4;
}bs;
/* 位域调用，赋值大小应当小于位数能表示的最大数
 * 超过这个数时编译器会产警告 
 */
bs.a;
bs->b;
```

#### **15. typedef**

```c
/* typedef 来定义别名 */
typedef unsigned char BYTE;
BYTE b1, b2;

typedef struct Books {
    char title[50];
    int book_id;
} Book;
Book b1;
/* typedef vs define
 * typedef 仅限于为类型定义符号名称
 * #define 不仅可以为类型定义别名，也能为数值定义别名，比如可以定义 1 为 ONE
 * typedef 是由编译器执行解释的，#define 语句是由预编译器进行处理的
 */
```

#### **16. 标准输入、输出、错误输出
`stdin` `stdout` `stderr`
读或输出字符：`getchar()` `putchar()`
读或输出一行：`gets()` `puts()`
格式化输入输出：`scanf()` `printf()`

```c
/* 文件读写 */
FILE *fopen(const char *filename, const char *mode);
/* 模式:
 * r 只读，文件不存在程序出错
 * w 只写，文件不存在则创建，存在截为0
 * a 增加写入，文件不存在则创建
 * r+ 读写，文件不存在程序出错，存在截为0
 * w+ 读写，文件不存在则创建，存在截为0
 * a+ 读写增加，文件不存在则创建
 * b 二进制模式
 */
int fputc(int c, FILE *fp);
int fputs(const char *str, FILE *fp);

int fgetc(FILE *fp);
char *fgets(char *buf, int n, FILE *fp);

/* 读写二进制 */
size_t fread(void *ptr, size_t size, size_t numbers, FILE *fp);
size_t fwrite(const void *ptr, size_t size, size_t numbers, FILE *fp);
```

#### **17.预处理器**

```c
/*
 * #define   定义宏
 * #include  包含一个源代码文件
 * #ifdef    如果宏已经定义，返回真
 * #ifndef   如果宏未定义，返回真
 * #if       如果条件为真，则编译下方代码
 * #else
 * #elif
 * #endif    结束一个#if语句
 * #error    当遇到标准错误时，输出错误消息
 * #pragma   使用标准化方法，向编译器发布特殊命令到编译器中
 */
 
#define MAX_ARRAY_LENGTH 20
 
#include <stdio.h>
#include "myheader.h"
 
#undef FILE_SIZE
#define FILE_SIZE 42
 
#ifndef MESSAGE
   #define MESSAGE "You wish"
#endif

#ifdef DEBUG
    /* do something */
#else
    /* doing... */
#endif

/* # 号的使用使用传入宏的变量转为字符串
 * ## 号使两个参数合并
 */
#include <stdio.h>

#define tokenpaster(n) printf ("token" #n " = %d", token##n)

int main(void)
{
   int token34 = 40;
   
   tokenpaster(34);
   return 0;
}

/* 输出 */
token34 = 40
 
```

预定义的宏
`__DATE__` 以"MMM DD YYYY"表示的日期
`__TIME__` 以"HH:MM:SS"表示的时间
`__FILE__` 当前文件名
`__LINE__` 当前行号
`__STDC__` 当以ANSI标准编译时，定义为1

#### **18. 类型转换**

![强制类型转换](../../assets/images/强制类型转换.png)

#### **19. 可变参数**

```c
/* 可变参数定义在 stdarg.h 头文件中
 * 函数的第一个参数总是int，表示参数的个数，后面跟省略号
 * 使用int参数和va_start宏初始化va_list变量为参数列表
 * 使用va_arg宏和va_list变量来访问参数列表中的每一项
 * 使用va_end来清理赋予va_list变量的内存
 */
#include <stdio.h>
#include <stdarg.h>


double average(int num, ...)
{
    double sum = 0.0;
    va_list valist;
    va_start(valist, num);
    for (int i = 0; i < num; i++) {
        sum += va_arg(valist, int);
    }
    va_end(valist);
    return sum / num;
}

int main()
{
    double i = average(5, 1, 2, 3, 4, 5);
    printf("average is: %f\n", i);
    return 0;
}
```

#### **20. 内存管理**

```c
void *calloc(int num, int size);
void *malloc(int num);
void realloc(void *address, int newsize);
void free(void *address);
```

