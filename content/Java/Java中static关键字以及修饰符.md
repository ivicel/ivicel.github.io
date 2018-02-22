title: Java中static关键字以及修饰符
date: 2018-02-22
tags: java, 静态static, java修饰符



> `Java`类中的变量会按照定义的先后顺序来进行初始化, 并且优先于任何方法(包括构造方法)
>
> 另外, `static`变量会优先于普通变量进行初始化, `static`变量也是按顺序
>
> 只有`static`初始化完成, 普通变量才会初始化

#### 1. `static`修饰类

```java
// 修饰内部类时, 内部类是一个嵌套类, 不含有指向外部类的引用
// 只能使用外部类的 static 变量和方法
public class OutterClass {
  public OutterClass() {}
  
  public static class InnerClass {}
}   
```

#### 2. `static`修饰成员变量

```java
// 修饰类成员变量时, 变量值会在第一次访问类时被赋值, 第一次new, 第一次访问变量



class Bowl {
    Bowl(int marker) {
        System.out.println("Bowl(" + marker + ")");
    }

    void f1(int marker) {
        System.out.println("class Bowl: f1(" + marker + ")");
    }
}

class Table {
    static Bowl bowl1 = new Bowl(1);
    Table() {
        System.out.println("Table()");
        bowl1.f1(1);
    }

    void f2(int marker) {
        System.out.println("class Table: f2(" + marker + ")");
 	}
  
  	static Bowl bow2 = new Bowl(2);
}

class Cupboard {
    Bowl bowl3 = new Bowl(3);
    static Bowl bowl4 = new Bowl(4);
    Cupboard() {
        System.out.println("Cupboard()");
        bowl4.f1(2);
    }

    void f3(int marker) {
        System.out.println("Cupboard");
        bowl4.f1(2);
    }

    static Bowl bowl5 = new Bowl(5);
}

public class StaticTest {
    public static void main(String[] args) {
        System.out.println("Creating new Cupboard() in main.....first");
        new Cupboard();
        System.out.println("Creating new Cupborad() in main.....second");
        new Cupboard();
        table.f2(1);
        cupboard.f3(1);
    }
	
    static Table table = new Table();
    static Cupboard cupboard = new Cupboard();
}

// 输出
/*
Bowl(1)
Bowl(2)
Table()
class Bowl: f1(1)
Bowl(4)
Bowl(5)
Bowl(3)
Cupboard()
class Bowl: f1(2)
Creating new Cupboard() in main.....first
Bowl(3)
Cupboard()
class Bowl: f1(2)
Creating new Cupborad() in main.....second
Bowl(3)
Cupboard()
class Bowl: f1(2)
class Table: f2(1)
Cupboard
class Bowl: f1(2)
*/
```

在程序运行后, 首先会触发类`StaticTest`的两个`static`变量的初始化

`static Table table = new Table()`

这句会使类`Table`中的`static`变量初始化, 而后在`cupboard`的初始化中可以看到`static`的`bowl4` `bowl5`会优先非`static`初始化

`static Cupboard cupboard = new Cupboard()`

#### 3. `static`修饰代码块

```java
// static 在修饰代码块时同修饰成员方法是一样的, 只初始化一次
public class StaticTest {
  	static int n;
  	static int m;
  	
  	static {
      	n = 5;
      	m = 6;
    }
}
```

#### 4. `static`修饰类方法

`static `修饰的类方法可以使用`类名.方法名`进行访问, 相当一个全局方法. `static`方法只能访问`static`变量和调用 `static`方法


#### 5. `Java` 修饰类

| 修饰符         | 当前类  | 同一包内 | 子孙类  | 其他包  |
| ----------- | ---- | ---- | ---- | ---- |
| `public`    | Y    | Y    | Y    | Y    |
| `protected` | Y    | Y    | Y    | N    |
| `default`   | Y    | Y    | N    | N    |
| `private`   | Y    | N    | N    | N    |

