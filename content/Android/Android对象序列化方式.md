title: Android对象序列化方式
date: 2018-04-01
tags: android, 序列化, serializable, parceable



`Android`内序列化对象主要有两种方式, 一是原`Java`自带的`Serializable`接口, 二是`Android`内自有的`Parcelable`接口

### 1. `Serializable`接口

`Java`自带的序列接口使用非常简单, 只要实现`Serializable`接口即可. `Serializable`接口只是一个标志类, 系统会将实现了这个接口的类自动进行序列化. 

> 如果想自定义序列化/反序列化过程, 可以自主实现`writeObject()`和`readObject()`. 一般我们都不会这么做的

还可以定义一个`long serialVersionUID`来检测反序列时的数据. 如果值不一样, 反序列时出抛出错误. 这个值可以使用`Android Studio`自动生成, 也可以手工指定一个. 数值不论如何, 其本质是一样的.

实现`Serializable`的类成员也一定是可以`Serializable`的, 比如基本类型`int`, `long`, 字符类型`String`, 或者实现了`Serializable`接口的自定义类. 

可以使用关键字`transient`来标明不参与序列化过程的变量

```java
public class User implements Serializable {
 	// 定义一个数值以便验证反序列化时的数据正确性
    private static final long serialVersionUID = 8711368828010083044L;
    
    // 使用关键字 transient 表示变量不参与序列化过程
    private int age;
    
    // 要序列化的变量
    private String name;
    private boolean isMale;
    
    // getter and setter
    // .....
}
```



### 2. `Parcelable`接口

由`Parcelable`序列化的类可以自由在`Binder`中进行传输. 但实现的过程会比`Serializable`麻烦些. 但是`Serializable`在序列化和反序列化时需要大量的`I/O`操作, 效率会比较低. 在`Android`中推荐使用`Parcelable`, 其在内存中序列化后可以立马发送到网络中, 或者保存到设备上. 如果数据较小也可以使用`Serializable`来实现, 其优点是方便简单

可`Parcelable`类里内的变量需要是基本类型或者是可序列化的对象. `Intent`, `Bundle`, `Bitmap`都实现了`Parcelable`接口. `List`, `Map`如果其内的每个元素是可序列化的话, 那么这两个也是可序列化的.



实现`Parcelable`要实现几个方法和变量:

1. `writeToParcel(Parcel out, int flag)`方法的实现表示类是如何创建序列化对象和数组的. **注意这个实现是的顺序, 当反序列化时也需要按这个顺序来写**
   `flags`的值一般为`0`或`1`(即`PARCELABLE_WRITE_RETURN_VALUE`), 当为`1`时表示当前对象需要作为返回值返回, 不能立即释放资源. **通常一般这个值都为`0`**
2. `describeContents()`方法的返回值一般为`0`, 当序列化内容含有**文件描述符**时, 返回`1`(即`CONTENTS_FILE_DESCRIPTOR`)
3. 定义一个`static final`的常量`CREATOR`来实现反序列化操作. 这个常量实现了`Parcelable.Creator`接口.
   `T createFromParcel(Parcel in)`方法表明如何反序列化一个类. **反序列化的顺序要和序列化时一样**
   `T[] newArray(int size)`方法表明如何反序列化出一个类的对象数组



```java
public class User implements Parcelable {
 	private int id;
    private String name;
    // 要注意自定义的类也得是可序列化的
    private Book book;
    
    public User(int id, String name, Book book) {
     	this.id = id;
        this.name = name;
        this.book = book;
    }
    
    // getter and setter
    // .....
    
 	public int describeContents() {
        // 一般返回 0, 除非有文件描述符存在才返回 1
     	reutrn 0;   
    }
    
    public void writeToParcel(Parcel out, int flags) {
        // 序列化的过程, 注意其序列, 在反序列化时要一致
        // flags 一般传入值为0, 只有在当有需要不能立即释放资源时才会传入 1
        out.wirteInt(id);
        out.writeString(name);
        out.writeParcelable(book, 0);
    }
    
    public static final Parcelable.Creator<User> CREATOR = 
        	new Parceable.Creator<User>() {
    	public User createFromParcel(Parcel in) {
            // 反序列化过程
            return new User(in);
        }
        
        // 反序列化数组时的过程
        public User[] newArray(int size) {
            return new User[size];
        }
        
        // 反序列化的过程需要注意和序列化时的顺序一致
        private User(Parcel in) {
            int id = in.readInt();
            int name = in.readString();
            // 需要一个 classLoader 来加载类
            // 可以从当前线程加载类中查找, 或者指一个类加载
            // Book book = in.readParcel(Book.class.getClassLoader())
            Book book = in.readParcel(
                Thread.currentThread().getContextClassLoader());
        }
    }
}
```





##### Reference:

1. <<Android 开发艺术探索>>
2. https://developer.android.com/reference/android/os/Parcelable.html