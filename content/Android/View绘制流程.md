Title:  View绘制流程
Date: 2018-02-22
Tags: android, view绘制



* 一.  `view`的`MeasureSpec`测量取值

1. 对于`DecorView`其大小要求要`ViewRootImpl`中测量

   1. 如果要求`MACTH_PARENT`,就设置为窗口的大小`windowSize`, 模式为精确`EXACTLY`
   2. 如果要求为内容大小`WRAP_CONTENT`, 就设置为窗口大小`windowSize`, 模式为至多`AT_MOST`, 表示不能超过子`view`这个大小
   3. 默认设置为要求的大小`rootDimension`, 模式为精确`EXACTLY`

   ```java
   // ViewRootImpl#getRootMeasureSpec
   private static int getRootMeasureSpec(int windowSize, int rootDimension) {
           int measureSpec;
           switch (rootDimension) {
           case ViewGroup.LayoutParams.MATCH_PARENT:
               // Window can't resize. Force root view to be windowSize.
               measureSpec = MeasureSpec.makeMeasureSpec(windowSize, MeasureSpec.EXACTLY);
               break;
           case ViewGroup.LayoutParams.WRAP_CONTENT:
               // Window can resize. Set max size for root view.
               measureSpec = MeasureSpec.makeMeasureSpec(windowSize, MeasureSpec.AT_MOST);
               break;
           default:
               // Window wants to be an exact size. Force root view to be that size.
               measureSpec = MeasureSpec.makeMeasureSpec(rootDimension, MeasureSpec.EXACTLY);
               break;
           }
           return measureSpec;
       }
   ```
```

   ​

2. 普通子`view`的大小要受到父`ViewGroup`的`MeasureSpec.getMode`的值(`UNSPECIFIED`, `EXACTLY`, `AT_MOST`)影响.子`view`的大小指子`view`的**内容+左右`margin`+左右`padding`值**

![子view的MeasureSpec](../images/子view的MeasureSpec.png)

子`view`的测量要从父`ViewGroup`开始, 在`ViewGroup#measureChildWithMargins`中, 如果这个`view`支持`margin`, `padding`的话

​```java
// ViewGroup#measureChildWithMargins

protected void measureChildWithMargins(View child,
            int parentWidthMeasureSpec, int widthUsed,
            int parentHeightMeasureSpec, int heightUsed) {
        final MarginLayoutParams lp = (MarginLayoutParams) child.getLayoutParams();

        final int childWidthMeasureSpec = getChildMeasureSpec(parentWidthMeasureSpec,
                mPaddingLeft + mPaddingRight + lp.leftMargin + lp.rightMargin
                        + widthUsed, lp.width);
        final int childHeightMeasureSpec = getChildMeasureSpec(parentHeightMeasureSpec,
                mPaddingTop + mPaddingBottom + lp.topMargin + lp.bottomMargin
                        + heightUsed, lp.height);

        child.measure(childWidthMeasureSpec, childHeightMeasureSpec);
    }

// 在计算 margin, padding 后, 调用 getChildMeasureSpec 来获得子 view 大小和模式 
// 然后进行子 view 测量循环

// ViewGroup#getChildMeasureSpec
// 该方法结果取值为上表

public static int getChildMeasureSpec(int spec, int padding, int childDimension) {
        int specMode = MeasureSpec.getMode(spec);
        int specSize = MeasureSpec.getSize(spec);
  
		// 去掉 margin 和 padding 之后的大小, 负值表示超出父 ViewGroup, 则取 0
        int size = Math.max(0, specSize - padding);

        int resultSize = 0;
        int resultMode = 0;

        switch (specMode) {
        // Parent has imposed an exact size on us
        case MeasureSpec.EXACTLY:
            if (childDimension >= 0) {
                resultSize = childDimension;
                resultMode = MeasureSpec.EXACTLY;
            } else if (childDimension == LayoutParams.MATCH_PARENT) {
                // Child wants to be our size. So be it.
                resultSize = size;
                resultMode = MeasureSpec.EXACTLY;
            } else if (childDimension == LayoutParams.WRAP_CONTENT) {
                // Child wants to determine its own size. It can't be
                // bigger than us.
                resultSize = size;
                resultMode = MeasureSpec.AT_MOST;
            }
            break;

        // Parent has imposed a maximum size on us
        case MeasureSpec.AT_MOST:
            if (childDimension >= 0) {
                // Child wants a specific size... so be it
                resultSize = childDimension;
                resultMode = MeasureSpec.EXACTLY;
            } else if (childDimension == LayoutParams.MATCH_PARENT) {
                // Child wants to be our size, but our size is not fixed.
                // Constrain child to not be bigger than us.
                resultSize = size;
                resultMode = MeasureSpec.AT_MOST;
            } else if (childDimension == LayoutParams.WRAP_CONTENT) {
                // Child wants to determine its own size. It can't be
                // bigger than us.
                resultSize = size;
                resultMode = MeasureSpec.AT_MOST;
            }
            break;

        // Parent asked to see how big we want to be
        case MeasureSpec.UNSPECIFIED:
            if (childDimension >= 0) {
                // Child wants a specific size... let him have it
                resultSize = childDimension;
                resultMode = MeasureSpec.EXACTLY;
            } else if (childDimension == LayoutParams.MATCH_PARENT) {
                // Child wants to be our size... find out how big it should
                // be
                resultSize = View.sUseZeroUnspecifiedMeasureSpec ? 0 : size;
                resultMode = MeasureSpec.UNSPECIFIED;
            } else if (childDimension == LayoutParams.WRAP_CONTENT) {
                // Child wants to determine its own size.... find out how
                // big it should be
                resultSize = View.sUseZeroUnspecifiedMeasureSpec ? 0 : size;
                resultMode = MeasureSpec.UNSPECIFIED;
            }
            break;
        }
        //noinspection ResourceType
        return MeasureSpec.makeMeasureSpec(resultSize, resultMode);
    }
```



* #### 二. `View`的工作流程

`view`的测量分两种情况, 没有子`view`的测量, 另一种是测量`ViewGroup`, 此时需要再递归测量

1. 当测量`view`时会调用`View#measure`, 该方法是`final`不能重写. 如果`view`没有测量过或者是需要重新测量的, 该方法会调用`View#onMeasure`, 如有需要可以重写`View#onMeasure`, **注意, 如果需要`view`支持`padding`属性则需要在此处理**

```java
// View#onMeasure

protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
  	// getSuggestMinimumXXX 主要是检测是否设置了背景, 如果设置了取
  	// mMinXXX 和 background.mMinXXX 的中的最大值. 没有设置则取 mMinXXX
  	// mMinXXX 由 xml 中的 android:minHeight, android:minWidth 来设置
	
	setMeasuredDimension(
      	getDefaultSize(getSuggestedMinimumWidth(), widthMeasureSpec),
		getDefaultSize(getSuggestedMinimumHeight(), heightMeasureSpec));
}

// View#getDefaultSize

public static int getDefaultSize(int size, int measureSpec) {
      int result = size;
      int specMode = MeasureSpec.getMode(measureSpec);
      int specSize = MeasureSpec.getSize(measureSpec);

      switch (specMode) {
        // 该值多用于系统控件的测量
        case MeasureSpec.UNSPECIFIED:
            result = size;
            break;
        // 一般自定义 view 时使用这两个选项
        case MeasureSpec.AT_MOST:
        case MeasureSpec.EXACTLY:
            result = specSize;
            break;
      }
      return result;
  }

// View#getSuggestMinimumWidth

// 如果 view 没有背景, 返回 android:minWidth, 默认为0
// 如果 view 有背景, 返回 背景的最小宽度 和 android:minWidth 中的最大值 
// 高度下同
protected int getSuggestedMinimumWidth() {
    return (mBackground == null) ? mMinWidth : 
  			max(mMinWidth, mBackground.getMinimumWidth());
}

// View#getSuggestMinimumHeight

protected int getSuggestedMinimumHeight() {
	return (mBackground == null) ? mMinHeight : 
  			max(mMinHeight, mBackground.getMinimumHeight());
}
```

一般自定义`view`多使用`AT_MOST`, `EXACTLY`来指定大小

这样其`specWidth`, `specHeight`就决定其宽/高度的大小. 所以当我们直接继承`View`来自定义`view`时, 如果设置`view`的宽/高为`wrap_content`时, 结合上表中的值, 可以知道如果我们不测量该`view`内容的大小, 其最终的大小为父`ViewGroup`的大小, 和设置`match_parent`一样. 可以使用以下的方法解决

```java
// 重写该 view 的 onMeasure, 测量内容大小

protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
 	super.onMeasure(widthMeasureSpec, heightMeasureSpec);
  	
  	int widthMeasureMode = MeasureSpec.getMode(widthMeasureSpec);
  	int widthMeasureSize = MeasureSpec.getSize(widthMeasureSpec);
  
  	int heightMeasureMode = MeasureSpec.getMode(heightMeasureSpec);
  	int heightMeasureSize = MeasureSpec.getSize(heightMeasureSpec);
	
  	// mWidth, mHeight 是自己设定的一个默认的宽/高度
  	ViewGroup.LayoutParams lp = getLayoutParams();
  	int width = (widthSpecMode == MeasureSpec.AT_MOST && 
        lp.width == ViewGroup.LayoutParams.WRAP_CONTENT) ? mWidth : widthMeasureSize;
	int height = (heightSpecMode == MeasureSpec.AT_MOST &&
		lp.height == ViewGroup.LayoutParams.WRAP_CONTENT) ? mHeight : heightMeasureSize;
	setMeasuredDimension(width, height)
}
```

2. `ViewGroup`的`measure`过程. 对于`ViewGroup`来说, 除了要测量自己的大小外, 还有递归的测量各个子元素的大小. 由于不同的布局其测量方法定义不同, 所以`ViewGroup`没有默认的`onMeasure`方法, 而是需要具体的继承类来实现该方法. `onMeasure`中调用`measureChildren`或是`measureChildWithMargins`来测量子类

   **需要注意的是如果不需要子`view`支持`margin`时, 使用`ViewGroup#measureChildren`来测量, 否则应当使用`ViewGroup#measureChildWithMargins`, 自定义的`ViewGroup`在重写`onMeasure`时需要特别注意**

   ```java
   // ViewGroup#measureChildren

   // measureChild 主要递归的调用 view#measure 来测量子 view
   // 的大小, 如果 view 不为 View.GONE 的话
   protected void measureChildren(int widthMeasureSpec, int heightMeasureSpec) {
       final int size = mChildrenCount;
       final View[] children = mChildren;
       for (int i = 0; i < size; ++i) {
           final View child = children[i];
           if ((child.mViewFlags & VISIBILITY_MASK) != GONE) {
               measureChild(child, widthMeasureSpec, heightMeasureSpec);
           }
       }
   }

   protected void measureChild(View child, int parentWidthMeasureSpec,
           int parentHeightMeasureSpec) {
       final LayoutParams lp = child.getLayoutParams();

       final int childWidthMeasureSpec = getChildMeasureSpec(parentWidthMeasureSpec,
               mPaddingLeft + mPaddingRight, lp.width);
       final int childHeightMeasureSpec = getChildMeasureSpec(parentHeightMeasureSpec,
               mPaddingTop + mPaddingBottom, lp.height);

       child.measure(childWidthMeasureSpec, childHeightMeasureSpec);
   }
   ```

   ​

   `layout`过程. 当`ViewGroup`的位置确定后, 其会调用`layout`, 并在其中调用 `onLayout`来遍历子`view`的`layout`方法来确定子`view`的位置. 子`view`的`layout`会调用自己的`onLayout`方法. `ViewGroup`没有默认实现`onLayout`, 交给具体的布局来实现, 以方法实现不同的布局

   ​

   ```java
   // ViewGroup#layout

   @Override
   public final void layout(int l, int t, int r, int b) {
       if (!mSuppressLayout && (mTransition == null || 			
   			!mTransition.isChangingLayout())) {
           if (mTransition != null) {
               mTransition.layoutChange(this);
           }
           super.layout(l, t, r, b);
       } else {
           // record the fact that we noop'd it; request layout when transition finishes
           mLayoutCalledWhileSuppressed = true;
       }
   }

   // View#layout

   public void layout(int l, int t, int r, int b) {
       if ((mPrivateFlags3 & PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT) != 0) {
           onMeasure(mOldWidthMeasureSpec, mOldHeightMeasureSpec);
           mPrivateFlags3 &= ~PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT;
       }

       int oldL = mLeft;
       int oldT = mTop;
       int oldB = mBottom;
       int oldR = mRight;

       boolean changed = isLayoutModeOptical(mParent) ?
               setOpticalFrame(l, t, r, b) : setFrame(l, t, r, b);

       if (changed || (mPrivateFlags & PFLAG_LAYOUT_REQUIRED) == PFLAG_LAYOUT_REQUIRED) {
           onLayout(changed, l, t, r, b);

           if (shouldDrawRoundScrollbar()) {
               if(mRoundScrollbarRenderer == null) {
                   mRoundScrollbarRenderer = new RoundScrollbarRenderer(this);
               }
           } else {
               mRoundScrollbarRenderer = null;
           }

           mPrivateFlags &= ~PFLAG_LAYOUT_REQUIRED;

           ListenerInfo li = mListenerInfo;
           if (li != null && li.mOnLayoutChangeListeners != null) {
               ArrayList<OnLayoutChangeListener> listenersCopy =
                       (ArrayList<OnLayoutChangeListener>)li.mOnLayoutChangeListeners.clone();
               int numListeners = listenersCopy.size();
               for (int i = 0; i < numListeners; ++i) {
                   listenersCopy.get(i).onLayoutChange(this, l, t, r, b, oldL, oldT, oldR, oldB);
               }
           }
       }

       mPrivateFlags &= ~PFLAG_FORCE_LAYOUT;
       mPrivateFlags3 |= PFLAG3_IS_LAID_OUT;

       if ((mPrivateFlags3 & PFLAG3_NOTIFY_AUTOFILL_ENTER_ON_LAYOUT) != 0) {
           mPrivateFlags3 &= ~PFLAG3_NOTIFY_AUTOFILL_ENTER_ON_LAYOUT;
           notifyEnterOrExitForAutoFillIfNeeded(true);
       }
   }
   ```



​	绘制过程`draw`. 绘制过程主要分为1.绘制背景`background.draw(canvas)`, 2.绘制自己`onDraw`, 3.绘制`children`.`dispatchDraw`方法, 4. 绘制装饰`onDrawScrollBars`. 主要调用`View#draw`方法

​	在`View`中有一个`View#setWillNotDraw`方法, 设置`true`表示不绘制该`view`. 默认为`false`. 当继承`ViewGroup`时, 需要手动设置为`false`关闭该标志位以便通过`onDraw`来绘制`view`

