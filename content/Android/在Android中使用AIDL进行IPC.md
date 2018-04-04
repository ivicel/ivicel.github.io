title: 在Android中使用AIDL进行IPC
date: 2018-04-01
tag: aidl, ipc, 进程间通信



##### `AIDL`基本介绍

`AIDL`全称`Android Interface Define Language`, 后缀名是`.aidl`. 其支持以下几个数据类型

* 基本数据类型`int`, `float`, `long`, `double`, `byte` , `short`, `boolean`, `char`
* `String`类型和`CharSequence`类型
* `List`类型,  并其内**元素**可以是**泛型**. 但元素一定是可`Parcelable`类型或是其他`AIDL`支持的类型. 可选择将 `List` 用作 “通用” 类（例如，`List<String>`）。另一端实际接收的具体类始终是 `ArrayList`，但生成的方法使用的是 `List` 接口。
* `Map`类型. 并其内元素不能是泛型, 元素一定`AIDL`支持的类型, 或者可`Parcelable`或者其他`AIDL`接口. 不支持通用 `Map`（如`Map<String,Integer>` 形式的 Map）。 另一端实际接收的具体类始终是 `HashMap`，但生成的方法使用的是 `Map` 接口。



一般有两种`.aidl`文件. 一种是定义可`Parcelable`的数据结构. 一种是定义方法接口.数据结构需要由我们自己来实现, 一般也会写在包内. 而接口方法由系统生成固定的接口, 然后在需要的地方再实现具体的业务逻辑, 实现该接口即可

一般我们会把`AIDL`文件全部都定义在一个`package`内. 这样才发送给客户端时, 只需把整个包发给他就 OK了. 但即使在同一个包内的`aidl`文件在使用其他包内的数据时也是要`import`才行.

在接口方法中定义的参数都必须带有`tag`标志们, `Primitives`基本类型和`String`和`CharSequence`默认是`in`而且只能是`in`. 其他可以为`in`, `out`, `inout`. 后面详解这三个`tag`

##### `AIDL`简单使用示例

首先定义两个`AIDL`文件

```aidl
// Book.aidl
package info.ivicel.github.aidldemo;

// 注意是小写
parcelable Book;
```

```aidl
package info.ivicel.github.aidldemo;

// 非基本数据类型需要导入
import info.ivicel.github.aidldemo.Book;

interface BookManager {
    // 测试不同的 tag 标志的影响
    // 返回值不需要 tag
    Book addBookIn(in Book book);
    Book addBookOut(out Book book);
    Book addBookInout(inout Book book);
}
```

再定义`Book.aidl`的实现`Book.java`. 需要注意的两点: 
一是如果把`Book.java`定义在`aidl`包中, 一定要向`build.gradle`添加查找`java`文件的路径.

```gradle
android {
	// .....
	sourceSets {
		main {
			java.srcDirs = ['src/main/java', 'src/main/aidl']
		}
	}
	// .....
}
```

二是默认的`Parcelable`接口并不要求实现`readFromParcel`方法, 但在`AIDL`中, `tag`标签的`out`,`inout`需要其来实现写入流, 如果不实现这个方法, 则只能为`in`

```java
package info.ivicel.github.aidldemo;


import android.os.Parcel;
import android.os.Parcelable;

// 如果 java 的实现类是放在和 aidl 同一个包内
// 一定不能忘了把 java 源码的路径加入到 build.gradle 中, 否则会找不到文件

public class Book implements Parcelable {
    private String name;
    private int price;

    // 需要显示的定义一个无参的 constructor
    public Book() {}
    
    // getter and setter...

    protected Book(Parcel in) {
        readFromParcel(in);
    }

    public static final Creator<Book> CREATOR = new Creator<Book>() {
        @Override
        public Book createFromParcel(Parcel in) {
            return new Book(in);
        }

        @Override
        public Book[] newArray(int size) {
            return new Book[size];
        }
    };

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeInt(price);
        dest.writeString(name);
    }

    // 默认的 Parcelable 是没有规定要实现 readFromParcel 方法
    // 但如果不实现这个方法, Book 的 tag 只能为 in
    public void readFromParcel(Parcel dest) {
        price = dest.readInt();
        name = dest.readString();
    }
}
```

以上三个文件`Book.aidl`, `Book.java`, `BookManager.aidl`在`client`和`server`端都必须有一份.

在`rebuild`,或是`clean`之后, 会在应用目录`build/source/aidl`下生成同名接口的`java`文件. 我们只要在`server`端根据具体的业务逻辑实现该接口中的方法即可. 然后使用`Service`来监听来自`client`的请求. 在`client`端来调用接口中的方法与`server`端进行通信

在`Server`端实现一个`Service`

```java
// AIDLService.java
public class AIDLService extends Service {
    private static final String TAG = "AIDLService";

    private List<Book> books = new ArrayList<>();

    // 由 AIDL 文件生成的 BookManager 接口的实现
    // 一般会有多个 client 连接到 server, 所以需要对 server 中的数据处理同步问题
    private final BookManager.Stub bookManager = new BookManager.Stub() {
        @Override
        public List<Book> getBooks() throws RemoteException {
            synchronized (this) {
                if (books != null) {
                    return books;
                }
            }
            return new ArrayList<>();
        }

        @Override
        public Book getBook() throws RemoteException {
            synchronized (this) {
                if (books == null) {
                    return null;
                }

                Random r = new Random(System.currentTimeMillis());
                int n = r.nextInt(books.size());
                return books.get(n);
            }
        }

        @Override
        public int getBookCount() throws RemoteException {
            synchronized (this) {
                if (books != null) {
                    return books.size();
                }
            }

            return 0;
        }

 		// ... 
    };

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "onCreate: ");
        Book book = new Book();
        book.setName("Android开发艺术探索");
        book.setPrice(28);
        books.add(book);

        book = new Book();
        book.setName("Android编程权威指南");
        book.setPrice(55);
        books.add(book);
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        Log.d(getClass().getSimpleName(), String.format("on bind, intent = %s", intent.toString()));
        return bookManager;
    }
}

```

然后在`Manifest.xml`中定义`Service`, 如果`Client`是另一个程序的话, 需要定义一个隐式的`Intent-filter`来通知`Service`接收什么连接

```xml
<!-- exported=true 表示能让非同应用的进程访问 -->
<!-- 为了安全最好还是定义一个 permission, 让拥有权限的应用访问 -->
<service
         android:name=".AIDLService"
         android:exported="true">
    <intent-filter>
        <!-- 定义一个 action, client 请求时使用, 需一致 -->
        <action android:name="info.ivicel.github.aidldemo.aidl"/>
        <!-- 定义一个 category, java 代码中系统会自动给添加上一个 DEFAULT -->
        <!-- 不定义会导致无法指收到请求. 或者定义其他的的 category -->
        <category android:category="android.intent.category.DEFAULT"/>
    </intent-filter>
</service>
```



在`Client`端, 我们可以通过`bindService()`来获得`BookManager`的引用

```java
// client 
// MainActivity.java 
public class MainActivity extends AppCompatActivity {
    
    private BookManager bookManager;
    private boolean bound = false;
    private ServiceConnection connection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
			// 在 bindService 之后我们就可以拿到 binder
            // 转为在 aidl 中定义好的接口, 就可以使用接口的方法
            bookManager = BookManager.Stub.asInterface(service);
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            bound = false;
            bookManager = null;
        }
    };
    
 	@Override
    protected void onCreated(Bundle saveInstanceState) {
     	super.onCreated(saveInstanceState);
        setContentView(R.layout.activity_main);
        
        if (!bound) {
            attempToBindService();
        }
    }
    
    private void attempToBindService() {
     	Intent intent = new Intent();
        intent.setAction("info.ivicel.github.aidldemo.aidl");
        intent.setPackage("info.ivicel.github.aidldemo");
        bindService(intent, connection, Context.BIND_AUTO_CREATE);
    }
    
    @Override
    protected void onDestroy() {
        super.onDestory();
        if (bound) {
            unbindService(connection);
        }
    }
}
```



##### `AIDL`方法参数`in`, `out`, `inout`意义

这三个参数表示的是数据的流向, 都是从`client`来看`server`.

* `in`表示数据从`client`流向`server`. `server`会从`client`接收到一个完整的对象, 但对该对象的修改不会使`client`端产生变化
* `out`表示数据从`server`流向`client`. `server`端会从`client`端接收到一个空对象, 对该对象的操作将反应到`client`传入的对象
* `inout`表示数据可双向流动, 以上两点的结合. 接收完整信息并反馈回`client`

依旧使用上一个例子来做一个实验

在`client`中使用三个不同的`tag`向`server`添加新的对象, 并在`server`中对其进行修改. 然后分别返回这个新的值. 这些过程都打对象打印出来作对比

```java
// client
private void addBookIn() {
    if (checkServerService()) {
        return;
    }

    Book book = new Book();
    book.setName("new_book_in");
    book.setPrice(20);
    try {
        Log.d("OnClient", "before addBookIn client book = " + book);
        Book b2 = bookManager.addBookIn(book);
        Log.d("OnClient", "addBookIn return from server: " + b2);
        Log.d("OnClient", "after addBookIn client book = " + book);
    } catch (RemoteException e) {
        e.printStackTrace();
    }
}

private void addBookOut() {
    if (checkServerService()) {
        return;
    }

    Book book = new Book();
    book.setName("new_book_out");
    book.setPrice(21);
    try {
        Log.d("OnClient", "before addBookOut client book = " + book);
        Book b2 = bookManager.addBookOut(book);
        Log.d("OnClient", "addBookOut return from server: " + b2);
        Log.d("OnClient", "after addBookOut client book = " + book);
    } catch (RemoteException e) {
        e.printStackTrace();
    }
}

private void addBookInout() {
    if (checkServerService()) {
        return;
    }

    Book book = new Book();
    book.setName("new_book_inout");
    book.setPrice(22);
    try {
        Log.d("OnClient", "before addBookInOut client book = " + book);
        Book b2 = bookManager.addBookInout(book);
        Log.d("OnClient", "addBookInOut return from server: " + b2);
        Log.d("OnClient", "after addBookInOut client book = " + book);
    } catch (RemoteException e) {
        e.printStackTrace();
    }
}

// server 
private static final BookManager.Stub bookManager = new BookManager.Stub {
 	// ....
    // 在 server 中, 分别都对传入进来的 book 名称加上 "_by_server`, 价格加 10, 然后返回
    @Override
    public Book addBookIn(Book book) throws RemoteException {
        Log.d("OnServer", "addBookIn: " + book);
        book.setName(book.getName() + "_by_server");
        book.setPrice(book.getPrice() + 10);
        books.add(book);
        return book;
    }

    @Override
    public Book addBookOut(Book book) throws RemoteException {
        Log.d("OnServer", "addBookOut: " + book);
        book.setName(book.getName() + "_by_server");
        book.setPrice(book.getPrice() + 10);
        books.add(book);
        return book;
    }

    @Override
    public Book addBookInout(Book book) throws RemoteException {
        Log.d("OnServer", "addBookInOut: " + book);
        book.setName(book.getName() + "_by_server");
        book.setPrice(book.getPrice() + 10);
        books.add(book);
        return book;
    }
}
```

`server`端打印的结果:

> OnServer: addBookIn: Book{name='new_book_in', price=20}
> OnServer: addBookOut: Book{name='null', price=0}
> OnServer: addBookInOut: Book{name='new_book_inout', price=22}

可以看出来, `tag`为`in`时, 传进来的是一个完整的对象数据值. 为`out`时, 传进来的是一个默认初始化的对象. 为`inout`传进来的也是一个完整对象

`client`端的打印结果:

首先是`tag`为`in`时. 返回的值说明`server`对对象有修改, 但`client`本身的原对象未发生变化. 说明`server`端是一个副本

> OnClient: before addBookIn client book = Book{name='new_book_in', price=20}
> OnClient: addBookIn return from server: Book{name='new_book_in_by_server', price=30}
> OnClient: after addBookIn client book = Book{name='new_book_in', price=20}

当`tag`为`out`时, `server`接收到的是一个默认初始化的对象, 数据并不同于`client`端, 但在`server`修改后, `client`会同步变化

> OnClient: before addBookOut client book = Book{name='new_book_out', price=21}
> OnClient: addBookOut return from server: Book{name='null_by_server', price=10}
> OnClient: after addBookOut client book = Book{name='null_by_server', price=10}

当`tag`为`inout`时, 是以上两种的结合

> OnClient: before addBookInOut client book = Book{name='new_book_inout', price=22}
> OnClient: addBookInOut return from server: Book{name='new_book_inout_by_server', price=32}
> OnClient: after addBookInOut client book = Book{name='new_book_inout_by_server', price=32}



代码地址: [GitHub](https://github.com/ivicel/dev-android-samples/tree/master/AIDL-Demo)



#### Reference:

1. https://blog.csdn.net/luoyanglizi/article/details/51980630
2. https://blog.csdn.net/luoyanglizi/article/details/51958091
3. https://blog.csdn.net/luoyanglizi/article/details/52029091
4. <<Android 开发艺术探索>>
5. https://developer.android.com/guide/components/aidl.html?hl=zh-cn