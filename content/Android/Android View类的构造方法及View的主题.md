title: Android View类的构造方法及View的主题属性优先级相关
date: 2018-04-22
tags: view, 构造方法, attrs, declare-styleable, style



### 1. layout 里 view 的属性赋值

一个 layout 文件里的 view 的属性可以在 5 个地方赋值, 优先级从高到低如下:

 * layout 中对属性直接赋值  
 * layout 中覆盖 view 的 style 
 * 构造方法里的 defStyleAttr 
 * 构造方法里的 defStyleRes, 这个当仅当 defStyleAttr 值为 0 , 或者其指定的 attr 值找不到(比如没设定)
 * 定义/使用的主题里的值 

1. 在 **layout** 布局文件里对 view 直接赋值

   ``` xml
   <TextView
   	android:textColor="#332211"/>
   ```

2. 自定义一个 `style`, 然后在 `layout` 里的 `view` 使用 `style` 属性来覆盖. 

   影响该 `view` 以及其子 `view`. 只有 `view` 有对应属性时才进行替换

   ```xml
   <style name="MyTextStyle">
       <item name="android:textColor">
   </style>
   <!-- 直接对 view 使用 -->
   <TextView
   	style="@style/MyTextStyle"/>
   <!-- 对 ViewGroup 使用, 影响子 view -->
   <LinearLayout
   	style="@style/MyTextStyle">
       
   	<TextView
   		android:text="inherit from ViewGroup textColor"/>  
       
       <!-- 没有 textColor 属性, 无影响 -->
       <ImageView
   		android:src="@drawable/welcome.png"/>
   </LinearLayout>
       
   ```

3. Default Style Attribute (defStyleAttr)

   在 `TextView` 的源代码里有一个构造方法是这样的

   ```java
   public TextView(Context context, @Nullable AttributeSet attrs) {
       this(context, attrs, com.android.internal.R.attr.textViewStyle);
   }
   ```

   `com.android.internal.R.attr.textViewStyle` 是一个 frameworks 层定义的 [attr](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/master/core/res/res/values/attrs.xml). 

   ```xml
   <resources>
       <!-- These are the standard attributes that make up a complete theme. -->
       <declare-styleable name="Theme">
           <!-- ... -->
           <!-- Default TextView style. -->
           <attr name="textViewStyle" format="reference" />
           <!-- .... -->
   	<declare-styleable>
   </resources>
   ```

   可以看到这个 attr 类型是一个引用, 所以当我们这样定义一个 style item 时

   ```xml
   <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
       <item name="android:textColor">@android:color/holo_green_dark</item>
       <!-- 由于 defStyleAttr 的优先级比主题的高, 
   		所以 textColor 被覆盖为 holo_blue_light, 即使上面定义了 textColor
   	-->
       <item name="android:textViewStyle">@style/BlueTextStyle</item>
   </style>

   <style name="BlueTextStyle">
       <item name="android:textColor">@android:color/holo_blue_light</item>
   </style>
   ```

4. Default Style Resource (defStyleRes)

   构造方法 `public View(Context context, AttributeSet attrs, int defStyleAttr, int defStyleRes)` 是在 SDK 21 之后才有的, 但 defStyleRes 的值是早之前就有使用的. 这个是一个 `R.style.[name]` 值, 只有当 defStyleAttr 为 0 或者查找不到时才有效

   > 需要注意的是, `defStyleAttr` 里要求的是一个 format="reference" 的 attr, 但其实质上是一个整型值, 并且代码中没有用 @AttrRes 来注释, 所以随便传一个整型值时, 便可能是相当于 defStyleAttr 不存在. 同理 `defStyleRes` 要求的是一个 style id

5. 在主题文件里赋值, 比如我们在 `styles.xml` 里自定义了一个主题 `AppTheme`. 

   这个主题可以在 `activity` 里覆盖, 也可以设置为程序的默认主题

   ``` xml
   <!--比如我们在 styles.xml 里自定义一个主题, 覆盖 andorid:textColor 后, 
   	使用该主题的 view 中有 android:textColor 这个属性的会使用我们设定的值
   	因为我们定义的是一个应用的主题, 而不是单独某个 view 下的某些个属性
   	所以这个主题需要继承系统的主题, 然后再覆盖, 下面继承的是 support 包里的兼容主题
    -->
   <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
       <item name="android:textColor">@color/myTextColor</item>
   </style>

   <!-- 设置好一个程序的主题文件后, 我们可以在 AndroidManifest.xml 中引用 -->
   <!-- 应用全局主题 -->
   <application
   	android:theme="@style/AppTheme"/>

   <!-- 在 activity 配置里引用, 这会覆盖掉全局 application 里的设置 -->
   <activity
   	android:theme="@style/AppTheme"/>
   ```



### 2. 构造方法介绍

以 SDK 27 中的 `ImageView` 为例, 一共有 4 个构造方法, 如下

```java
public ImageView(Context context) {
        super(context);
        initImageView();
}

public ImageView(Context context, @Nullable AttributeSet attrs) {
    this(context, attrs, 0);
}

public ImageView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
    this(context, attrs, defStyleAttr, 0);
}

public ImageView(Context context, @Nullable AttributeSet attrs, int defStyleAttr,
        int defStyleRes) {
    super(context, attrs, defStyleAttr, defStyleRes);
    /* .... */
}
```

构造方法最多有 4 个参数, 简单意思如下:

* `context` 每个构造方法都有, 用来 inflate, 获取各种参数值等. 如果我们从 Java 代码中直接创建一个新的 view, 一般都是使用只有 context 的参数的构造方法
* `attrs` 这个是对布局文件 layout.xml 里的解析后生成的对象, 可以获取到 xml 里的配置
* `defStyleAttr` 属性引用
* `defStyleRes` SDK 21 后增加的. 如果 minSdkVersion > 21 时才使用这个参数. 不然使用 `Theme#obtainStyledAttributes()` 也可以解析


在 View inflate 后, 其所以设置属性都解析到了参数 attrs 中. 可以通过 `AttributeSet#getAttributeName()`, `AttributeSet#getAttributeValue()` 来获得名称和值. 但这个获得的只能是直接的值, 如果像 `android:text=@string/name"` 这样引用, android 内部都是通过 id 来查找, 所以也是获得一个 id 值, 所以我们总是用 `Theme` 类里的方法来一步解析, 这样可以直接找到对应的 string 值而不是 id

> `Context` 中也有对应的方法, 其实质是调用了 context.getTeme.obtainStyledAttributes 而已

```java
// 从解析好的 AttributeSet 查找
TypedArray obtainStyledAttributes(AttributeSet set, int[] attrs, int defStyleAttr, 
		int defStyleRes)
// 从主题中查找
TypedArray obtainStyledAttributes(int[] attrs)
// 从指定的资源文件查找
TypedArray obtainStyledAttributes(int resId, int[] attrs)
```




### Reference:

1. [http://www.jcodecraeer.com/a/anzhuokaifa/androidkaifa/2016/0806/4575.html](http://www.jcodecraeer.com/a/anzhuokaifa/androidkaifa/2016/0806/4575.html)
2. [https://blog.csdn.net/nbalichaoq/article/details/50550103](https://blog.csdn.net/nbalichaoq/article/details/50550103)