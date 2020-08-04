---
title: "Android Contnet Provider内容提供器"
date: 2018-02-22
tags: ["android", "content provider", "内容提供器"]
categories: ['Android']
cover: "/images/markus-spiske.jpg"
---

[TOC]

### 1. Content Provider 的优势:

1. 可以用来提供进程间的通信
2. 提供一个统一的接口, 屏蔽了底层的具体实现. 底层可以使用数据库如`SQLite`, 文件, 或者从网络中获取
3. 提供了一个`权限`限制

### 2. Content URI 的写法:

> `content://` + `AUTHORITY` + `/表名`
>
> `content://com.example.myapp.provider/table1`
>
> `AUTHORITY`一般默认写成`包名.provider`, `包名.provider类名`, 一般用包名在前修饰, 以免在需要共享给别的程度时产生冲突
>
> 后面跟表名, 或者还可以跟修饰符`*`, `#`,

书写规则

`*`表示匹配任意长度任意字符

> `content://com.example.myapp.provider/*` 查询所有表中所有数据

`#`表示匹配任意长度的数字

> `content://com.example.myapp.provider/table1/#`
>
> 查询`table1`中的某一行, 如果提供了这类`MIME_TYPE`的话, 可以使用
>
> `content://com.example.myapp.provider/table/3`访问表`table`的第`3`行数据
>
> 此时可以使用类`ContentUris`添加一个`id`, 类`Uri#withAppendedPath`也是一样, 只不过接收的是一个`String`类型
>
> `Uri singleUri = ContentUris.withAppendedId(MyProvider.CONTENT_URI, id)`

#### `MIME`的写法

---

> 1. 必须以`vnd`开头
> 2. 如果以内容 URI 结尾的, 后面接`android.cursor.item/`; 如果以目录 URI 结尾的, 后面接`android.cursor.dir/`
> 3. 最后接上`vnd.<authority>.<path>`

例如: `vnd.android.cursor.dir/vnd.com.example.myapp.provider/table1`

`ContentResolver`类中有两个预定义的`vendor`

`ContentResolver.CURSOR_ITEM_BASE_TYPE = "vnd.android.cursor.item"`

`ContentResolver.CURSOR_DIR_BASE_TYPE = "vnd.android.cursor.dir"`

#### 在`AndroidManifest.xml`中写法

---

当非同一个程序中需要使用`Content Provider`时, 必须要在`AndroidManifest.xml`声明使用权限. 比如读写用户字典:`<use-permission name="android.permission.READ_USER_DICTIONARY>`

然而如果在同一程序中, 无论是否声明自定义权限, 原程序都有其读写的权限

```xml
<provider
          android:authorities="list" // 要和类中定义的认证名完全一样
          android:directBootAware=["true" | "false"] // unlock deivce之前进行启动privoder
          andorid:enabled=["true" | "false"] // 启用
          android:exported=["true" | "false"] // 外部是否可访问到
          android:grantUriPermissions=["true" | "false"] // 可授予特定的uri临时权限. 如果true, 则可以授予权限给任意uri. false则只能授予权限给特定uri. 默认false
// 特定的uri权限在<grant-uri-permission>中声明
          android:icon="drawable resource" // 设置一个调用时的图标, 默认是application icon
          android:initOrder="integer" // 同一进程中的content provider初始顺序, 默认是从大的数字先初始
          android:label="string resource" // 默认使用application label
          android:multiprocess=["true" | "false"] // 在程序使用多进程情况下, true表示各进程生成各自的content provider object. false表示共用. 默认false
          android:name="string" // provider的名称. 一般取作 package.UserDictionaryProvider, 后面是provider的用处
          android:permission="string" // 设置一个读写权限名
          android:readPermission="string" // 读权限, 覆盖掉 android:permission 如果有
          android:wirtePermission="string" // 写权限, 覆盖掉 android:permission 如果有
		  andorid:process="string" // 进程的名称. 用来表示需要哪个进程来运行这个content provider					       // 一般情况下所有的 application components 都运行在同一进程下							// components 都有自己的 process 属性来表示需要运行在不同的进程当中					 // 如果以一个分号(:)开头的进程名, 表示运行在一个程序私有新进程中						  // 如果直接以名字, 则表示运行在一个全局共享可访问的进程中
          android:syncable=["true" | "false"]> // 表示 content provider 底层数据是否是 synchronized

  // 在<provider>标签中还能包含<meta-data>, <grant-uri-permission>, <path-permission>标签
  // path-level permission中定义的权限会覆盖掉 application-level 中<permission>定义和provider-level 中的权限
  // 而 grant-uri-permission是对临时uri的权限, 不受这三个level的影响
  // 总体下说, 下层的权限覆盖总是对上层权限更加的精确把控, 需要精确分层时使用

</provider>

<provider android:name=".MyProvider"
          android:authorities="com.example.myapp.MyProvider"
          android:enable="true"
          android:exported="false"/>


```

#### 创建一个自定义的`Content Provider`

--------------------------------------;

1. 自定义一个类继承`ContentProvider`, 实现`onCreate`, `query`, `insert`, `update`, `delete`, `getType`方法
2. 使用`UriMatcher`类快速生成或者匹配`uri`

```java

public class MyProvider extends ContentProvider {

  	public static final String AUTHORITY = "com.example.myapp.MyProvider";
  	private static UriMatcher sUriMatcher;

  	private static final int SEARCH_WORDS = 0;
  	private static final int GET_WORD_DEFINITION = 1;
  	private static final int SEARCH_SUGGEST = 2;

  	public static final String WORD_MIME_TYPE =
      	ContentResolver.CURSOR_DIR_BASE_TYPE +
      	"/vnd.com.example.myapp.dictionary";
  	public static final String DEFINITION_MIME_TYPE =
  		ContentResolver.CURSOR_ITEM_BASE_TYPE +
      	"/vnd.com.example.myapp.dictionary";
  	public static final String SEARCH_SUGGEST_MIME_TYPE =
      	ContentResolver.CURSOR_DIR_BASE_TYPE +
      	"vnd.com.example.myapp.search_suggest";

  	// 生成匹配的对应 uri 的 mime type
  	static {
      	sUriMatcher = new UriMatcher(UriMatcher.NO_MATCH);
      	// search words
      	sUriMatcher.addURI(AUTHORITY, "dictionary", SEARCH_WORDS);
      	sUriMatcher.addURI(AUTHORITY, "dictionary/#", GET_WORD_DEFINITION);
      	sUriMatcher.addURI(AUTHORITY, "search_suggest", SEARCH_SUGGEST);
    }

    @Override
    public boolean onCreate() {
      	// 在第一次调用ContentResolver访问时会调用该方法
        // 返回true表示创建成功
        return true;
    }

    @Nullable
    @Override
    public Cursor query(@NonNull Uri uri, @Nullable String[] projection,
            @Nullable String selection,
            @Nullable String[] selectionArgs, @Nullable String sortOrder) {
        return null;
    }

    @Nullable
    @Override
    public String getType(@NonNull Uri uri) {
      	switch (sUriMatcher.match(uri)) {
          	case SEARCH_WORDS:
        		return WORD_MIME_TYPE;
          	case GET_WORD:
            	return DEFINITION_MIME_TYPE;
	        case SEARCH_SUGGEST:
            	return SEARCH_SUGGEST_MIME_TYPE;
            default:
            	throw new IllegalArgumentException("Unknown URL: " + uri);
        }
    }

    @Nullable
    @Override
    public Uri insert(@NonNull Uri uri, @Nullable ContentValues values) {
      	// insert to database/file
      	// return new rows uri
        return null;
    }

    @Override
    public int delete(@NonNull Uri uri, @Nullable String selection,
            @Nullable String[] selectionArgs) {
      	// delete datas
      	// return how many rows were deleted
        return 0;
    }

    @Override
    public int update(@NonNull Uri uri, @Nullable ContentValues values,
            @Nullable String selection,
            @Nullable String[] selectionArgs) {
      	// update something
      	// return how many
        return 0;
    }
}

```

#### 除了使用`ContentResolver`外, 其他几种访问`Content Provider`方法

---

-   `Batch access`

提供了一种批量处理方法, 首先生成一个`ArrayList<ContentProviderOperation>`数组, 向数组中添加所需操作, 然后使用`ContentResolver.applyBatch(ArrayList)`来调用这个批处理事件. 这会使`ContentResolver`调用`ContentProvider#applyBatch`方法, 可以在自定义`ContentProvider`时覆写这个方法, 其原始方法只是调用了`ContentProviderOperation#apply()`方法

在**Google Sample**中 [Contact Manager][!https://android.googlesource.com/platform/development/+/master/samples/contactmanager/] 示例中文件 [`ContacAdder.java`][!https://android.googlesource.com/platform/development/+/master/samples/contactmanager/src/com/example/android/contactmanager/contactadder.java] 演示批处理的用法

-   `Loader`

因为 `SimpleCursorAdapter`的弃用, 现在使用`Loader`来异步加载数据, 其能根据 `Activity` `Fragment` 的生命周期来控制数据获取周期, 以免造成**ANR**, 或者是重复加载数据

-   `Data access via intents`

使用`Intent`可以间接的访问到你没有获得权限的`Content Provier`.

> 需要在`AndroidManifest.xml`中的`<provider>`提供`android:grantUriPermission="true"`
>
> 或者`<grant-uri-permission>`中提供的可授权许可

比如在`MyApp`中提供调用相机程序的拍照功能 , 在`MyApp`中自定义一个`FileProvider`来提供路径地址来存储获得的照片(`Internal Storage`或`External Storage`), 然而由于访问程序私有路径是非法的, 需要获得相应的授权.

此时我们就可以在调用相应的`Intent`时, 使用`Context#grantUriPermission()`加上`Content.FLAG_GRANT_READ_URI_PERMISSION`或是`Content.FLAG_GRANT_WRITE_URI_PERMISSION`授予该`uri`(仅仅是针对该**URI**, 并不是整个`Content Provider`)临时权限, 在调用的`Intent`返回结束, 为保证安全, 调用 `Context#revokeUriPermission()`来取消掉这个权限.

> Tips: `FileProvider`在 4.4 以上会自动授权

又例如, 即使没有声明`Manifest.permission.READ_CONTACTS`, 也可以使用一个`Intent.ACTION_PICK`来挑选个联系人加上`ContactsContrac.RawContacts.CONTENT_ITEM_TYPE`这个`uri`来获取一个联系人信息. 由于这些操作是在前台`UI`上执行的, 用户可以看到并且选择联系人是自己操作的, 相当用户同意授予了其读取联系人的权限

#### `Contract Classses`

---

所谓`Contract Classes`是一些定义了一些`constants`, `content URIs`, `column names`, `intent actions`

例如`UserDictionary.Words.CONTENT_URI`, `UserDictionary.Words`, `ContactsContract`
