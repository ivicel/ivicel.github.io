title:  Android 代码 values 目录下说明
date: 2018-04-22
tags: resources, android资源文件, attrs, style, styleable
cover: ../../assets/images/candy-bomber.jpg



对于 Android 源代码目录下 `values/*` 文件, 其所有的 xml 文件根标签都是 `resource`. aapt 会把这个目录下的文件全部 build  出 java 可引用的整型数值, 这样的便可以通过 `R.[type].[name]` 来引用到. 其类型只和标签名有关, 对放在哪个文件无关. 一般我们会把这些个类型不同的分别放在不 `values/*` 下不同的文件里只是为了方便编码时自己查看.一般有以下几种类型:

### 1. style 主题文件

主题文件一般有两种, 一个是 `style`, 一个是属性 `attr`

1. style 标签是主题文件. 一般我们会从系统中的主题, 或者是某个 view 来继承. 或者也可以自己单独写而不继承. **style 标签里 item 的 name 值需要已经是有定义过了的, 可以是系统预先定义好的, 或者是自己再使用 attr 定义的.** 使用 `R.style.[name]` 来引用. 在 xml 文件中使用 `style=@style/[name]` . 一般放在 `values/styles.xml`

   ```xml
   <!-- 自定义主题并继承 support 包里的主题 
   	继承的主题可以在 3 个地方使用, 全局 application, 单个 activity, 某个 view	
    -->
   <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
       <!-- 覆写 support 主题里的值 -->
       <item name="colorPrimary">@color/colorPrimary</item>
       <!-- 覆写系统主题里的值, 这其实是一个 framework 里的内部 attr -->
       <item name="android:textViewStyle">@style/BlueTextStyle</item>
       <!-- 覆写系统主题里的值 -->
       <item name="android:textSize">18sp</item>
       <!-- 自定义的属性值 -->
       <item name="source_name">sources</item>
   </style>
   <attr name="source_name" format="string"/> 
   <!-- 自定义的 style, 可以在 layout 中的 view 直接引用 style=@style/BlueTextStyle -->
   <style name="BlueTextStyle">
       <item name="android:textColor">@android:color/holo_blue_light</item>
   </style>
   ```

2. 使用 attr 的原因是为自定义 view 添加属性, 另外是方便更改属性的值. 有两种定义方式. 

   一种是直接在 `resources` 下定义

   ```xml
   <resources>
       <attr name="one" format="reference"/>
   </resources>
   ```

   一种是在外面包一层 `declare-styleable` 标签. 

   ```xml
   <!-- 引用整组为 R.styleable.MyAttrs, 单个为 R.styleable.MyAttrs_other_one -->
   <resources>
       <declare-styleable name="MyAttrs">
           <!-- 这个是 attr 的定义 -->
   	    <attr name="other_one" format="reference"/>
           <!-- 这个是对已经定义的 attr 引用, 没有 format 值 -->
           <attr name="one"/>
   	</declare-styleable>
   </resources>
   ```

   使用 `declare-styleable` 主要有两点

   * 它提供了一个数组的引用 `R.styleable.[styleable-name]` 引用(组里成员引用为 `R.styleable.[styleable-name]_[attr-name]` 注意组名和成员名是用下划线_连接) 由于在使用 `Theme#obtainStyledAttributes()` 的参数, 如果我们直接引用 `R.attr.one` 也是要组成一个数组的
   * 如果我们有不同的自定义的 view, 比如 MyTextView, MyOtherTextView, 这样使用分组便于管理

   #### attr 属性的 format 取值

   > 当 attr 中没有 format 值时, 是对已经定义了的 attr 的引用

   1. `reference` 引用. 某个资源 ID.

      ```xml
      <attr name="my_bg" format="reference"/>

      <TextView
      	app:my_bg="@drawable/bg"/>
      ```

   2. `color` 颜色值.

   3. `boolean` 布尔值

   4. `dimension` 尺寸值

   5. `float` 浮点数

   6. `integer` 整型

   7. `string` 字符串

   8. `fraction` 百分数. 使用时类似系统 `android:pivotX="200%"`

   9. `enum` 枚举类型. 使用时只能取一个惟一值. 

      ```xml
      <declare-styleable name="MyDirection"> 
          <attr name="orientation"> 
              <enum name="horizontal" value="0" /> 
              <enum name="vertical" value="1" /> 
          </attr>
      </declare-styleable>
      ```

   10. `flag` 标志位, 使用时通过 `|` 竖线来设置单个或多个值, 如 `stateOne | stateTwo` 这样

       ```xml
       <declare-styleable name="MyState"> 
           <attr name="windowSoftInputMode"> 
               <flag name="stateOne" value="0x01" /> 
               <flag name="stateTwo" value="0x10" /> 
           </attr>
       </declare-styleable>


       ```

   11. 混合类型, 比如支持 `string|reference` 这种, 使用 `|` 竖线分隔开

### 2. 其他资源文件

1. [Bool](https://developer.android.com/guide/topics/resources/more-resources.html#Bool) 布尔型, 只有(true/false)两个值

   使用 `R.bool.[name]`, `@bool/[name]` 来引用. 一般存放在 `values/bools.xml`. 

```xml
<resources>
    <bool name="screen_small">true</bool>
</resources>
```
2. [Color](https://developer.android.com/guide/topics/resources/more-resources.html#Color) 颜色, 一个 16 进制的值(#*RGB*, #*ARGB*, #*RRGGBB*, #*AARRGGBB*). 跟 `res/colors` 下的区别是, 这里的值一般只存储单一的颜色值. 使用 `R.color.[name]`, `@color/[name]` 来引用, 存放在 `values/colors.xml`

```xml
<resources>
   <color name="opaque_red">#f00</color>
   <color name="translucent_red">#80ff0000</color>
</resources>
```
3. [Dimension](https://developer.android.com/guide/topics/resources/more-resources.html#Dimension) 长度尺寸, 有 dp, sp, pt, px, mm, in 单位. 最主要用到的是 `dp` 和 `sp`. `dp` 是一种与设备 DPI 无关的单位, 换算公式为 `px = dp * (dpi / 160)`. 一共有 `ldpi(120)`, `mdpi(160)`, `hdpi(240)`, `xhdpi(320)`, `xxhdpi(480)`, `xxxhdpi(640)`, `nodpi`, `tvdpi`. 通过 `DisplayMetrics#densityDpi` 来获取该设备的 dpi, `DisplayMetrics.density` 来获取比值, 即 **设备dpi / 基准dpi **(`DisplayMetrics.densityDpi / 160`). 使用 `R.dimen.[name]`, `@dimen/[name]` 来引用

> 注意: Android 只有以上几种 dpi 比值, 当设备 dpi 和上设定的不完全相等时, 会取近似值. 比如 165 取得 160

```xml
<resources>
    <dimen name="textview_height">25dp</dimen>
    <dimen name="font_size">16sp</dimen>
</resources>
```

4. [ID](https://developer.android.com/guide/topics/resources/more-resources.html#Id) 独一无二的 ID 值. 一般我们会在 layout 文件中直接用 `@+id/id_name` 来建立, 不过, 当我们有许多地方需要用到这个 id 时, 单独建立文件 `values/ids.xml` 来设置这个 id, 然后在需要的地方引用就可. 特别是 `ConstraintLayout` 这个需要前后引用 id 来设定 view 的位置时, 就减少了工作量, 不必总使用 `@+id/id_name` 来保证 id 一定存在了.  通过 `R.id.[name]`, `@id/[name]`  来引用. 存放在 `values/ids.xml`

  ```xml
  <resources>
      <item type="id" name="button_ok" />
  </resources>

  <!-- layout 中引用 -->
  <Button android:id="@id/button_ok"/>
  ```

5. [Integer](https://developer.android.com/guide/topics/resources/more-resources.html#Integer) 整数值, 通过 `R.integer.[name]`, `@integer/[name]` 来引用. 存放在 `values/integers.xml`

  ```xml
  <resources>
      <integer name="max_speed">75</integer>
  </resources>
  ```

6. [Integer Array](https://developer.android.com/guide/topics/resources/more-resources.html#IntegerArray) 整型数值, 通赤 `R.array.[name]` 来引用. 使用 java 来解析. `getResources().getInArray(R.array.bits)`. 存放在 `values/integers.xml`

  ```xml
  <resources>
      <integer-array name="bits">
          <item>4</item>
          <item>8</item>
          <item>16</item>
          <item>32</item>
      </integer-array>
  </resources>
  ```

7. [Typed Array](https://developer.android.com/guide/topics/resources/more-resources.html#TypedArray) 混合型数组, 可以引用其他的资源, 数组里可以是引用同一类型的值, 也可以是不同的类型, 当引用不同类型时, 在解析的时候就有注意判断类型值. 使用 `R.array.[name]` 引用, 然后有 Java 代码中使用 `obtainTypedArray()` 来解析具体的值. 存放在 `values/arrays.xml`

  ```xml
  <resources>
      <array name="icons">
          <item>@drawable/home</item>
          <item>@drawable/settings</item>
          <item>@drawable/logout</item>
      </array>
  </resources>
  ```

  java 解析代码示例

  ```java
  TypedArray icons = getResources().obtainTypedArray(R.array.icons);
  Drawable drawable = icons.getDrawable(0);
  ```

8. [String](https://developer.android.com/guide/topics/resources/string-resource.html) 字符串. 使用 `R.string.[name]`, `@string/[name]` 引用. 存放在 `values/strings.xml`

9. [String Array](https://developer.android.com/guide/topics/resources/string-resource.html) 字符串数组. 使用 `R.array.[name]`, `@string/name` 引用. 放在 `values/strings.xml`

   ```Xml
   <resources>
       <string-array name="planets_array">
           <item>Mercury</item>
           <item>Venus</item>
           <item>Earth</item>
           <item>Mars</item>
       </string-array>
   </resources>
   ```

10. [String Plurals](https://developer.android.com/guide/topics/resources/string-resource.html) 英文中的单复数形式

    ```xml
    <resources>
        <plurals name="numberOfSongsAvailable">
            <item quantity="one">Znaleziono %d piosenkę.</item>
            <item quantity="few">Znaleziono %d piosenki.</item>
            <item quantity="other">Znaleziono %d piosenek.</item>
        </plurals>
    </resources>
    ```

    ​