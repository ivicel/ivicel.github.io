---

title: "Android 动画分析"
date: 2018-05-01
tags: ["animator", "动画", "插值器", "interpolator", "animation"]
categories: ['Android']

---



Android 的动画分为以下两类:

1. View 动画
   * 补间动画(Tween Animation, `Animation` 类及其子类): 通过对 view 不断的作 rotate, scale, translate 等一系列操作从而达到动画效果, xml 文件放在 `res/anim/` 目录中
   * 帧动画(Frame Animation, `AnimationDrawable` 类): 通过播放一系列预先生成好的图片达到的动画效果, 像电影胶片一样, 因为是不断的更换图片, 容易产生 OOM, xml 文件放在 `res/drawable/` 目录中
2. 属性动画(Property Animation): 通过不断的改变 view 的各种属性而达到动画效果,  帧动画存放在 `res/animator/` 中

动画的定义可以由 xml 格式来定义, 也可以直接在 java 代码中直接生成. 然后在对应的 view 里调用动画的 start 方法



### 1. 补间动画(Tween Animation)

补间动画一共有 4 个动画方式, 对应 `Animation` 类下的 4 个子类, 也可以用 xml 格式来定义动画

* 平移标签 `<translate>`, 对应类 `TranslateAnimation`
* 缩放标签 `<scale>`, 对应类 `ScaleAnimation`
* 旋转标签 `<rotate>`, 对应类 `RotateAnimation`
* 透明度标签 `<alpha>`, 对应类 `AlphaAnimation`

> 在 drawable 中也有 scale, rotate 标签, 不过存放目录不同, 生成的 java 类也是不同(Drawable).

```xml
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android"
    android:interpolator="@[package:]anim/interpolator_resource"
    android:shareInterpolator=["true" | "false"] >
    <alpha
        android:fromAlpha="float"
        android:toAlpha="float" />
    <scale
        android:fromXScale="float"
        android:toXScale="float"
        android:fromYScale="float"
        android:toYScale="float"
        android:pivotX="float"
        android:pivotY="float" />
    <translate
        android:fromXDelta="float"
        android:toXDelta="float"
        android:fromYDelta="float"
        android:toYDelta="float" />
    <rotate
        android:fromDegrees="float"
        android:toDegrees="float"
        android:pivotX="float"
        android:pivotY="float" />
    <set>
        ...
    </set>
</set>
```

* `<set>` 代表一个动画组, 可以包括单个/多个动画, 或者包含其他动画组. 对应类 `AnimationSet`
  * `android:interpolator` 插值器. 本质上就是定义动画如何变化的数学函数, 变化规律
  * `andorid:shareInterpolator` 是否在子组中共享插值器. 不共享时子动画需要自己指定
* `<alpha>` 淡入/淡出标签
  * `android:fromAlpha` 开始值
  * `android:toAlpha` 结束值
* `<scale>` 缩放标签
  * `android:fromXScale` 横坐标开始值
  * `android:toXScale` 横坐标结束值
  * `android:fromYScale` 纵坐标开始值
  * `andorid:toYScale` 纵坐标结束值
  * `android:pivotX` 缩放中心的 x 坐标
  * `android:pivotY` 缩放中心的 y 坐标
* `<translate>` 平移标签
  * `android:fromXDelta` x 起始位置
  * `android:toXDelta` x 结束位置
  * `android:fromYDelta` y 起始位置
  * `android:toYDelta` y 结束位置
* `rotate` 旋转标签
  * `android:fromDegrees` 旋转开始的角度, 比如 0
  * `android:toDegrees` 旋转结束的角度, 比如 180
  * `android:pivotX` 旋转的中心点横坐标
  * `android:pivotY` 旋转的中心点纵坐标

通过 java 代码来启动动画

```java
ImageView iv = findViewById(R.id.image_view);
Animation animation = AnimationUtils.loadAnimation(this, R.anim.my_animation);
// 另外还可以设置动画时间, 动画完成后是否停留在结束位置
animation.setDuration(3000);
animation.setFillAfter(true);
iv.startAnimation(animation);
```

### 2. 帧动画(Frame Animation)

帧动画比较简单, 就是按规定的顺序来播放一系列的图片. 需要注意的是避免加载过多尺寸较大的图片从而引起 OOM. `animation-list` 对应的是类 `AnimationDrawable`, 可以跟多个 item

```xml
<?xml version="1.0" encoding="utf-8"?>
<animation-list xmlns:android="http://schemas.android.com/apk/res/android"
    android:oneshot=["true" | "false"] >
    <item
        android:drawable="@[package:]drawable/drawable_resource_name"
        android:duration="integer" />
</animation-list>
```

* `android:oneshot` 是否只播放一次动画
* `android:drawable` 图片来源
* `andorid:duration` 图片播放时间

```java
ImageView rocketImage = findViewById(R.id.rocket_image);
rocketImage.setBackgroundResource(R.drawable.rockets);

AnimationDrawable rocketAnimation = (AnimationDrawable) rocketImage.getDrawable();
rocketAnimation.start();
```

### 3. 属性动画(Property Animation)

属性动画是 SDK 11 之后加入的特性, 可以对任意的对象而不单单只是 view, 在一定的时间内(默认 300ms)把对象的属性从一个值变化到另一个值. 所以属性动画几乎无所不能. 属性动画对应的类为 `Animator`, 资源文件存在 `res/animator/` 中

```xml
<set
  android:ordering=["together" | "sequentially"]>
    <objectAnimator
        android:propertyName="string"
        android:duration="int"
        android:valueFrom="float | int | color"
        android:valueTo="float | int | color"
        android:startOffset="int"
        android:repeatCount="int"
        android:repeatMode=["repeat" | "reverse"]
        android:valueType=["intType" | "floatType"]/>

    <animator
        android:duration="int"
        android:valueFrom="float | int | color"
        android:valueTo="float | int | color"
        android:startOffset="int"
        android:repeatCount="int"
        android:repeatMode=["repeat" | "reverse"]
        android:valueType=["intType" | "floatType"]/>

    <set>
        ...
    </set>
</set>
```

* `<set>` 动画合集, 对应 `AnimatorSet` 类, 可以包含 `<objectAnimator>`, `<animator>`, `<set>` 等. 如果是子 set, 可以有自己的 `android:ordering`

  * `andorid:ordering` 动画的播放顺序. `together` 默认, 同时播放; `sequentially` 按顺序播放

* `<objectAnimator>` 可定义任意对象的属性动画, 对应 `ObjectAnimator` 类. 

  * `android:propertyName` 属性名, 比如 "alpha", "backgroundColor", 必须值. 定义之后, 类会通过反射去找对象时对应属性的 getter/setter 方法
  * `android:duration` 动画播放时间
  * `andorid:valueFrom` 开始值
  * `android:valueTo` 结束值
  * `android:valueType` 值的类型. 默认 `floatType`, 整型 `intType`

  > 注意开始, 结束值默认是 float 浮点值, 如果是颜色值也是用 float, 如果是 int 型, 需要自己手动设置

  * `android:startOffset` 调用 `ObjectAnimator#start()` 延迟多少毫秒后开始
  * `android:repeatCount` 重复多少次. `-1` 表示无限重复. 默认 `0` 表示只播放一次. `n` 表示一共播放 `n + 1`  次
  * `android:repeatMode` 重复播放时的模式. `repeat` 总是从头开头播放. `reverse` 反转播放, 头->尾->头->尾….这样的方式

* `<animator>` 可定义在一个指完时间内完成一系列动画. 对应类 `ValueAnimator`. 由于 `ObjectAnimator` 就是继承的 `ValueAnimator` 类, 所以 animator 中定义的值的意思是一样.

对于一个定义好的 xml, 可以使用 java 代码来启动动画

```java
AnimatorSet as = (AnimatorSet) AnimatorInflater.loadAnimator(myContext, R.animator.property_animator);
as.setTarget(myObject);
as.start();
```

### 4. 属性动画的监听器

属性动画主要有两个监听器 

```java
public interface AnimatorUpdateListener {
    // 开始, 结束, 取消, 重复时调用
    void onAnimationStart(Animator animator);
    void onAnimationEnd(Animator animator);
    void onAnimationCancel(Animator animator);
    void onAnimationRepeat(Animator animator);
}

public interface AnimatorListener {
 	// 动画播放每一帧时调用, 即是每一次值改变时调用
    // 这个有时会对一些没有 getter/setter 方法的属性有特别用处, 比如想设置从 0~100 的宽度
    // 可以设置成 0~100 的值变化, 然后在值每次变化时的回调, 更改其宽度
    void onAnimationUpdate(ValueAnimator animation);
}
```

### 5. 插值器(Interpolator)

插值器其实就是一类描述在指定时间内(默认 300ms)变化速率的函数 f(x), 其类都实现了 `android.view.animation.Interpolator` 接口. 主要有以下几种, 每个插值类都有对应的 xml 描述. `getInterpolation` 方法返回的是一个百分比.

```java
public interface Interpolator {
 	abstract float getInterpolation(float input);   
}
```

- `AccelerateDecelerateInterpolator` 动画从开始到结束，变化率是先加速后减速的过程。
- `AccelerateInterpolator` 动画从开始到结束，变化率是一个加速的过程。
- `AnticipateInterpolator` 开始的时候向后，然后向前甩
- `AnticipateOvershootInterpolator` 开始的时候向后，然后向前甩一定值后返回最后的值
- `BounceInterpolator` 动画结束的时候弹起
- `CycleInterpolator` 动画从开始到结束，变化率是循环给定次数的正弦曲线。
- `DecelerateInterpolator` 动画从开始到结束，变化率是一个减速的过程。
- `LinearInterpolator` 以常量速率改变
- `OvershootInterpolator` 向前甩一定值后再回到原来位置

### 6. 估值器(TypeEvaluator)

估值器是一个设置值变化的过程, 其参数 fraction 为从 interpolator 接收来的变化百分比, startValue 为初始值, endValue 为最终值, 返回计算后的结果. 默认的有颜色 `ArgbEvaluator`, 浮点数/浮点数组 `FloatEvaluator`/`FloatArrayEvaluator`, 整型/整型数组 `IntEvaluator`/`IntArrayEvaluator`, 坐标 `PoinFEvaluator`, 矩形 `RectEvaluator`. 如果不是这些类型的变化, 需要自己定义, 只需要实现 TypeEvaluator

> 如果不实现 TypeEvaluator, 也可以在监听 Interpolator 的变化时做出值的改变

```java
public interface TypeEvaluator<T> {
 	public T evaluate(float fraction, T starValue, T endValue);   
}
```




### Reference:

1. [https://developer.android.com/guide/topics/resources/animation-resource](https://developer.android.com/guide/topics/resources/animation-resource)
2. <<Android 开发艺术探索>>