title: Android View 的坐标系
date: 2018-04-28
tags: view, 坐标



屏幕的坐标原点为屏幕的左上角, 往右为**正向x轴**, 往下为**正向y轴**. 坐标参数顺序一般为`左`, `上`, `右`, `下`

子`view`可以获取其相对于父`ViewGroup`的坐标.  这个要跟点击事件`MotionEvent`的坐标获取方法区别开来

`view`由于是一个框模型, 所以当确定左上点和右下点的位置, 我们便可以确定一个`view`的大小和位置.
左上点坐标为 **(`View.getLeft()`, `View.getTop()`)**, 右下点坐标 **(`View.getRight()`, `View.getBottom()`)**

`view` 的大小: 

宽度 `width = getRight() - getLeft()` 

高度 `height = getBottom() - getTop()`

> 这也是 `getWidth()`, `getHeight()` 的算法. 其和 `getMeasuredWidth()`, `getMeasuredHeight()` 的差别主要在于后者一般是用于测量时获得的宽高, 并带有模式, 是 view 的原始大小. 一般情况下这两者对应的值是一样的, 不过 `getWidth()`, `getHeight()` 是在布局后(`onLayout`)才能获得, 有时可能某些 ViewGroup 在布局时更改了 view 的大小, 从而导致这两者的值不一样

`getLeft()`, `getTop()`, `getRight()`, `getBottom()` 这4个方法获得是`view`布局时的原始坐标, 其值在测量布局后不会再改变. 而一个`view`真正在屏幕显示的位置是其偏移量`translate`和**原始位置**共同决定的. 这其中我们只要确定左上点的位置便可. 其实际左上点位置关系为:

左上点横坐标: `float View.getX() = int View.getLeft() + float View.getTranslationX()`


左上点纵坐标: `float View.getY() = int View.getTop() + float View.getTranslationY()`

在引入了`Z轴`之后(**API 21**), `Z轴`关系为: `float View.getZ() = int View.getElevation() + float View.getTranslationZ()`

>  特别需要注意的是, 在 `activity` 中调用这些方法时, 得到的值是0, 因为此时 `view` 还未布局, 需要等要`view.onMeasure` 之后才会进行赋值. 

有4种方法来获取这些值.

1. 使用 `ViewTreeObserver`监听`view`的 Draw/Layout 事件
2. 将一个runnable添加到Layout队列中, 使用 `View.post`
3. 重写`view.onLayout`方法
4. 重写`Activity.onWindowFocusChange`方法

![view坐标](../../assets/images/view坐标.png)