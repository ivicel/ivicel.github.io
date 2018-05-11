Title: View 事件体系
Tags: view事件, view坐标, view滑动, view触摸
Date: 2018-02-22



#####  `view`坐标和滑动方法

* 触摸事件`MotionEvent`和`TouchSlop`

  单指触摸屏幕时, 一般会产生`MotionEvent.ACTION_DOWN`(手指接触屏幕时), `MotionEvent.ACTION_MOVE`(手指移动时), `MotionEvent.ACTION_UP`(手指离开屏幕时). 

  触摸事件产生时, 可以获取其位置.

  获取其相对**当前`View`**的位置: 相对左边`MotionEvent.getX()`, 相对上边`MotionEvent.getY()`

  获取共相对**屏幕**的位置: 相对屏幕左边`MotionEvent.getRawX()`, 相对屏幕上边`MotionEvent.getRawY()`

  `TouchSlop`为系统所能识别出的最小的距离, 其值由系统决定. 可以通过`ViewConfiguration.getScaledTouchSlop()`来获得

  ​

* 滑动速度追踪`VelocityTracker`


  滑动速度指的是在某一个时间段内的速度. 

  ```java
  /* 首先可以在 View 中的 onTouchEvent 内获得追踪事件 */
  VelocityTracker vt = VelocityTracker.obtain();
  vt.addMovement(event);
  /* 然后必须要先设定时间段以便计算出该时间内的速度, 最后再获取速度, 速度为负时表示向左滑动 */
  vt.computeCurrentVelocity(1000); 			//计算1000ms内的速度
  int xVelocity = (int)vt.getXVelocity();		//横向速度, 手指向左滑动为负
  int yVelocity = (int)vt.getYVelocity();		//纵向速度, 手指向上滑动为负
  /* 回收内存 */
  vt.clear();
  vt.recycle();
  ```

* 手势检测`GestureDetector`, 单击, 滑动, 长按, 双击

  ```java
  // 在view 里onTouchEvent中截断事件来进行监听
  GestureDetector mGestureDetector = new GestureDetector(context);
  // 设置是否需要长按
  mGestureDetector.setIsLongpressEnabled(false);
  return mGestureDetector.onTouchEvent(event);
  ```

  * `GestureDetector.OnGestureListener`接口
    1. `onDown`手指触摸到屏幕时.由一个`ACTION_DOWN`触发
    2. `onShowPress`手指触摸到屏但没有松开或者是移动, 一般用来给用户触摸找反馈, 高亮文本.由一个`ACTION_DOWN`触发.
    3. `onSingleTapUp`手指(在触摸后)松开, 单击行为. 伴随一个`MotionEvent.ACTION_UP`
    4. `onScroll`手指触摸屏幕后滚动, 由一个`ACTION_DOWN`和多个`ACTION_MOVE`触发
    5. `onLongPress`触摸后长按
    6. `onFling`按下屏幕后, 快速滑动后松开. 由一个`ACTION_DOWN`和多个`ACTION_MOVE`和一个`ACTION_UP`触发
  * `GestureDetector.OnDoubleTapListener`接口
    1. `onDoubleTap`双击. 不能和`onSingleTapConfirmed`共存
    2. `onSingleTapConfirmed`严格的单击行为. 如果触发了这个, 即使接下快速第二次触击也会被认为是一次单击而不是产生双击行为.
    3. `onDoubleTapEvent`表示发生了双击行为. 会依次调用`ACTION_DOWN`, `ACTION_MOVE`, `ACTION_UP`



* `view`的滑动方法. 

  1. 通过`view.scrollTo`和`view.scrollBy`方法滑动

     注意这两个方法滚动的**并非`view`本身**而是**`view`的内容**, 所以要想滑动某个`view`, 需要获取到其父`view`然后到父`view`进行滑动. 即`((View)childView.getParent()).scrollX`如此.

     `scrollBy`其中也是调用`scrollTo`来滑动, 只不过中内部进行了计算`scrollTo(offsetX + mScrollX, offsetY + mScrollY)`. 而`scrollTo`在内部调用了`invalidateInternal(left - mScrollX, top - mScrollY, right - mScrollX, bottom - mScrollY, true, false)`, 其中`left`, `top`, `right`, `bottom`为上次的坐标点. 所以当传入**负数**的时候才是向右移动

     `mScrollX`和`mScrollY`分别左内容边框到view左边框, 上内容边框到view上边框的大小, 可以通过`view.getScrollX()`, `view.getScrollY()`获得该值

  2. 通过动画给`view`施加平移效果

     这种方法便是通过改变`view`的`translationX`和`translationY`值. 

     老旧的动画方法并没有真的改变了`view`的位置, 所以在`view`"移动"到新位置时, 其一些比如单击事件并不能通过点击新位置产生. 这些可以使用属性动画解决, 而现在也只使用属性动画(Property Animator)

  3. 通过改变`view`的`LayoutParams`参数使得`view`重新布局

     比如发变`view`的`margin`等等, 或者通其一些关联的`view`做变化, 以便影响到目标`view`. 

     比如在一个垂直的`LinearLayout`, 上边是一个高度为0的`view`, 下面为目标`view`, 通过改变上边`view`的高度来使用目标`view`的高度发生变化

  4. 使用`Scroller`类.

     `Scroller`类是一个滑动的`Helper`类, 其本质上是使用`view.scrollTo`方法来滑动, 但内部有一个可定义`Interpolator`类, 即插值属性来提供滑动变动曲线, 使得滑动更加的流畅.


```Java
 /* 一般使用 Scroller 类来滚动 View 时, 都使用在自定义 View 中 
  * 在自定义 View 的构造方法获取一个 Scroller 实例
  * 然后重写 View.computeScroll 方法, 该方法会在重绘 view 时被调用
  * 在 View.computeScroll 中使用 Scroller.computeScrollOffset 来确认是否完成滑动
  * 若是没有完成, 则调用 View.scrollTo 来滑动 View 内容的位置, 然后再次调用 View.postInvalidate 方法促使 View 重绘以便再次检查滑动是否完成
  * 如此的反复回调直到滑动的完成
  */
 public class CustomView extends View {
   	private Scroller mScroller;
   
 	public CustomView(Context context, AttributeSet attrs, int defStyleAttr) {
       super(context, attrs, defStyleAtrr);
       mScroller = new Scroller(context);
     }
   
   	/* 提供一个外部使用的滚动方法, 参数为滚动的目标坐标, 同 view.scrollTo */
   	public void smoothScrollTo(int destX, int destY) {
       	int deltaX = destX - getScrollX();
       	int deltaY = destY - getScrollY();
       	/* 该方法并没有产生滑动, 而只是设置了一变量值, 比如初始位置和滑动距离, 滑动时间等 */
       	mScroller.startScroll(getScrollX(), getScrollY(), deltaX, deltaY);
       	/* 促使 view 进行重绘 */
       	invalidate();
     }
   
   	public void smoothScrollBy(int deltaX, int deltaY) {
     	smoothScrollTo(mScroller.getCurrX() + deltaX, mScroller.getCurrY() + deltaY);  
     }
   
   	@Override
   	public void computeScroll() {
         /* view 在绘制的时候会调用该方法
          * 此时我们调用 scroller.computeScrollOffset 来确认是否已经滑动到目标位置
          * 若是没有的话, 返回 true. 然后我们继续滑动 view 的位置 
          */
     	if (mScroller.computeScrollOffset()) {
         	/* 真正的滑动调用, mScroller.getCurrX(), getCurrY() 方法获得的是在设计时间 duration 时计算后的位置, 而 getFinalX() 则获得最终位置. */
           	scrollTo(mScroller.getCurrX(), mScroller.getCurrY());
           	/* 因为滑动可能还没有完成, 所以再次调用一次 view 重绘 */
           	postInvalidate();
         }
     }
 }
```



##### `view`事件的分发体系

同一事件序列是指手指接触屏幕的那一刻起, 到手指离开屏幕的进结束, 这其中产的一系列事件. 这包括`ACTION_DOWN`和0个或多个`ACTION_MOVE`和`ACTION_UP`事件. 

在默认不做特殊处理的情况下一个事件序列只能被一个`view`处理

`view`的事件分发首先由`Activity`最先捕获, 然后一层一层的分发到具体的子`view`, 如果中途没有被截断的话;

子`view`如果没有处理这个事件的话, 最后再沿路返回到`Activity`中.

首先看`Activity#dispatchTouchEvent`和`PhoneWindow#superDispatchTouchEvent`代码

```java
// Activity#dispatchTouchEvent

public boolean dispatchTouchEvent(MotionEvent ev) {
  	if (ev.getAction() == MotionEvent.ACTION_DOWN) {
      	/*
      	 * onUserInteraction() 是一个空方法, 可以覆写这个方法来检测用户与手机产生的交互
      	 * 对应的还有 onUserLeaveHint() 来检测用户手指离开了屏幕
      	 */
     	onUserInteraction(); 
    }
  	/*
  	 * Window 是一个抽象类, 其只有一个惟一的实现 PhoneWindow. 
  	 * PhoneWindow#superDispatchTouchEvent() 方法惟一作用就是把事件继续向下传递到 DecorView
  	 *
  	 */
  	if (getWindow().superDispatchTouchEvent(ev)) {
      	return true;
    }
    return onTouchEvent(ev);
}

/******************************************************/
// DecorView#superDispatchTouchEvent

public boolean superDispatchTouchEvent(MotionEvent ev) {
  	/* mDecor 即 DecorView 类 */
 	return mDecor.superDispatchTouchEvent(ev); 
}
```

`DecorView`继承了`FrameLayout`并实现了`RootViewSurfaceTracker`, `WindowCallbacks`. `DecorView`即是屏幕的总父`view`, 包括了标题栏和内容部分, 即是`setContentView`的父`view`. 其在接收到`view`事件后, 会继续向下派发, 由于`FrameLayout`并没覆写这个方法, 所以最终传到父`ViewGroup`来处理.   (~~这火传的2333333~~)

```java
public boolean superDispatchTouchEvent(MotionEvent ev) {
 	return super.dispatchTouchEvent(ev);
}
```

`ViewGroup#dispatchTouchEvent`. `ViewGroup`会判断是否要向下一层`view`传递事件, 这样一层一层如此循环, 最终完成整个事件的分发.

```java
// ViewGroup#dispatchTouchEvent

public boolean dispatchTouchEvent(MotionEvent ev) {
	/* ..... */
	/* 省略前面是一些事件的判断 */
  	boolean handled = false;
    if (onFilterTouchEventForSecurity(ev)) {
    	final int action = ev.getAction();
		final int actionMasked = action & MotionEvent.ACTION_MASK;

		// Handle an initial down.
      	// ACTION_DOWN 事件时, 重置所有的标志位
		if (actionMasked == MotionEvent.ACTION_DOWN) {
			// Throw away all previous state when starting a new touch gesture.	
          	// The framework may have dropped the up or cancel event for the previous gesture
			// due to an app switch, ANR, or some other state change.
			cancelAndClearTouchTargets(ev);
			resetTouchState();
		}

        final boolean intercepted;
        /* 这里检查 ViewGroup 是否要中断事件向下分发和调用 onIterceptTouchEvent
         * 当手指刚接触屏幕时为 ACTION_DOWN, 所以条件必然成立, 也就是说在不设置标志位下, 
         * ViewGroup 一定可以中断事件继续分发. 第二条件是 mFirstTouchTarget 的值.
         * 该变量指的是消费事件的 view, ACTION_DOWN时必为null, 如果派发成功, 
         * 在接下来的 ACTION_MOVE, ACTION_UP 则不会为 null 值
         *
         * 接下来则要判断拦截标志位. FLAG_DISALLOW_INTERCEPT 是由 
         * ViewGroup#requestDisallowInterceptTouchEvent 方法进行设置的,
         * 这样一来 ViweGroup 就不再拦截到该事件
         * 但 ACTION_DOWN 为例外, 因为 ViewGroup 会对该类事件做标志重置, 所以不管子 View 如何请求
         * ViewGroup 依然可以拦截到 ACTION_DOWN
         * 
         */
        if (actionMasked == MotionEvent.ACTION_DOWN || mFirstTouchTarget != null) {
            final boolean disallowIntercept = (mGroupFlags & FLAG_DISALLOW_INTERCEPT) != 0;
            if (!disallowIntercept) {
                intercepted = onInterceptTouchEvent(ev);
                ev.setActoin(action);
            } else {
                intercepted = false;
            }
        } else {
            intercepted = true;
        }
  	/* ......... */
    }
}
```

由以上可以看出, `ViewGroup#onInterceptTouchEvent`并不是每次都会被调用到

* 如果事件是`ACTION_DOWN`, 则一定会被调用

* 如果不是`ACTION_DOWN`, 则要考虑:

  1. 是否有了接收事件的目标子`view`. 没有的话,直接设置中断事件派发, 并且不会调用`onInterceptTouchEvent`

  2. 有了接收事件`view`, 则查看子`view`是否请求设置不要中断事件标志`ViewGroup#requestDisallowInterceptTouchEvent`.

     设置后则不调用; 没有设置则会调用`onInterceptTouchEvent`

`ViewGroup`只在**当为鼠标的左键(主按键)的按下事件并且屏幕能滚动时**才会中断事件的派发, 否则默认不中断分发事件 

```java
// ViewGroup#onInterceptTouchEvent

public boolean onInterceptTouchEvent(ev) {
	if (ev.isFromSource(InputDevice.SOURCE_MOUSE) &&
        ev.getAction() == MotionEvent.ACTION_DOWN &&
        ev.isButtonPressed(MotionEvent.BUTTON_PRIMARY) &&
        isOnScrollbarThumb(ev.getX(), ev.getY())) {
      	return true;
    }
  	return false;
}
```

`ViewGroup#dispatchTouchEvent`中如果没有中断派发时, 查找接收的子`view`, 如果查找到了, 就调用其`dispatchTouchEvent`, 没有找到则调用`super.dispatchTouchEvent`, 其实就是`View#dispatchTouchEvent`

来看`View#dispatchTouchEvent`的代码. 由于`View`作为`ViewGroup`的父类, 所以该方法作用在于两方面.

* 一是作为子`view`即像`TextView`之类时处理从`ViewGroup`派发下来的事件
* 二是作为`ViewGroup`的父类, 处理`ViewGroup#dispatchTouchEvent`(实际是在`ViewGroup#dispatchTransformedTouchEvent`)调用父类的`dispatchTouchEvent`时

```java
// View#dispatchTouchEvent
public boolean dispatchTouchEvent(MotionEvent event) {
 	if (event.isTargetAccessibilityFocus()) {
     	// We don't have focus or no virtual descendant has it, do not handle the event.
      	if (!isAccessibilityFocusedViewOrHost()) {
          	return false;
        }
      	// We have focus and got the event, then use normal event dispatch.
      	event.setTargetAccessibilityFocus(false);
    }
  
  	boolean result = false;
  	
  	if (mInputEventConsistencyVerifier != null) {
      	mInputEventConsistencyVerifier.onTouchEvent(event, 0);
    }
  
  	final int actionMasked = event.getActionMasked();
  	if (actionMasked == MotionEvent.ACTION_DOWN) {
     	// Defensive cleanup for new gesture
      	stopNestedScroll();
    }
  
  	if (onFilterTouchEventForSeCurity(event)) {
      	if ((mViewFlags & ENABLED_MASK) == ENABLED && handleScrollBarDragging(event)) {
         	return = true; 
        }
      	/* 
      	 * 这里会检查几个地方
      	 * 如果 view 在 enable (默认) 状态下
      	 * 并且设置了 onTouchListener 回调, 则调用 listener 的 onTouch 方法 
      	 *
      	 * 如果调用了 onTouch 方法, 该方法的返回值会对 View#onTouchEvent 方法产生影响
      	 * onTouch 返回 true 时则不会再调用 View#onTouchEvent 
      	 * 反之才会调用, 这样方便在 View 之外中断默认的处理方法, onTouch 方法优先级更高
      	 */
      	// noinspection SimplifiableIfStatement
      	ListenerInfo li = mListenerInfo;
      	if (li != null && li.mOnTouchListener != null &&
           	(mViewFlags & ENABLED_MASK) == ENABLED &&
           	li.mOnTouchListener.onTouch(this, event)) {
         	result = true; 
        }
      	// onTouch(如果调用了) 返回 false 则在这里回调了 View#onTouchEvent 方法
      	if (!result && onTouchEvent(event)) {
          	result = true;
        } 
    }
  
  	if (!result && mInputEventConsistencyVerifier != null) {
     	mInputEventConsistencyVerifier.onUnhandledEvent(event, 0);
    }
  
  	// Clean up after nested scrolls if this is the end of a gesture
  	// alse cancel it if we tried an ACTION_DOWN but we didn't want the rest
  	// of the gesture
  	if (actionMasked == MotionEvent.ACTION_UP ||
       	actionMasked == MotionEvent.ACTIOIN_CANCEL ||
    	(actionMasked == MotionEvent.ACTION_DOWN && !result)) {
      stopNestedScroll();
    }
  	return result;
}
```

来看 `View#onTouchEvent`

```java
// View#onTouchEvent

public boolean onTouchEvent(MotionEvent event) {
 	final float x = event.getX();
  	final float y = event.getY();
  	final int viewFlags = mViewFlags;
  	final int action = event.getAction();
  
  	// 检查是否可以单击或者长按或者是长按弹出菜单(类似鼠标右健)
  	final boolean clickable = ((viewFlags & (CLICKABLE) == CLICKABLE) ||
		(viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE) ||
      	(viewFlags & CONTEXT_CLICKABLE) == CONTEXT_CLICKABLE);
  
  	// 检查 view 是否是 disable 状态, 但即使 view 是 disable 
  	// 但是可 clickable 状态下也会消费掉该事件, 只是没任何反应而已
  	if ((viewFlags & ENABLED_MASK) == DISABLED) {
      	if (action == MotionEvent.ACTION_UP && (mPrivateFlags & PFLAG_PRESSED) != 0) {
          	setPressed(false);
        }
      	mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
      	// A disabled view that is clickable still consume the touch
      	// events, it just doesn't respond to them
      	return clickable;
    }
  	// 如果使用 setTouchDelegate 代理方法, 则执行该方法, 和 setOnTouchListener 一样
  	if (mTouchDelegate != null) {
      	if (mTouchDelegate.onTouchEvent(event)) {
          	return ture;
        }
    }
  
  	// TOOLTIP类似 hover 或者右键鼠标的状态
  	// 在这要注意一些如 ImageView 默认是不可点击的, 所以直接返回的 false
  	// 然后事件会回退到 ViewGroup 由 ViewGroup 来处理
  	// 但该 view 还是捕获到 ACTION_DOWN 
  	// 这里就要注意一个坑, 因为事件序列只会由某一个 View/ViewGroup 来处理掉,
  	// 所以像 ImageView 这样的不可点击时, 事件回退来 ViewGroup
  	// 这样一来, ACTION_DOWN 之后的该序列里的事件就不会再传递到 ImageView 来
  	if (clickable || (viewFlags & TOOLTIP) == TOOLTIP) {
        switch (action) {
            case MotionEvent.ACTION_UP:
                mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                if ((viewFlags & TOOLTIP) == TOOLTIP) {
                    handleTooltipUp();
                }
                if (!clickable) {
                    removeTapCallback();
                    removeLongPressCallback();
                    mInContextButtonPress = false;
                    mHasPerformedLongPress = false;
                    mIgnoreNextUpEvent = false;
                    break;
                }
                boolean prepressed = (mPrivateFlags & PFLAG_PREPRESSED) != 0;
                if ((mPrivateFlags & PFLAG_PRESSED) != 0 || prepressed) {
                    // take focus if we don't have it already and we should in
                    // touch mode.
                    boolean focusTaken = false;
                    if (isFocusable() && isFocusableInTouchMode() && !isFocused()) {
                        focusTaken = requestFocus();
                    }

                    if (prepressed) {
                        // The button is being released before we actually
                        // showed it as pressed.  Make it show the pressed
                        // state now (before scheduling the click) to ensure
                        // the user sees it.
                        setPressed(true, x, y);
                    }

                    if (!mHasPerformedLongPress && !mIgnoreNextUpEvent) {
                        // This is a tap, so remove the longpress check
                        removeLongPressCallback();

                        // Only perform take click actions if we were in the pressed state
                        if (!focusTaken) {
                            // Use a Runnable and post this rather than calling
                            // performClick directly. This lets other visual state
                            // of the view update before click actions start.
                            if (mPerformClick == null) {
                                mPerformClick = new PerformClick();
                            }
                            if (!post(mPerformClick)) {
                                performClick();
                            }
                        }
                    }

                    if (mUnsetPressedState == null) {
                        mUnsetPressedState = new UnsetPressedState();
                    }

                    if (prepressed) {
                        postDelayed(mUnsetPressedState,
                                ViewConfiguration.getPressedStateDuration());
                    } else if (!post(mUnsetPressedState)) {
                        // If the post failed, unpress right now
                        mUnsetPressedState.run();
                    }

                    removeTapCallback();
                }
                mIgnoreNextUpEvent = false;
                break;

            case MotionEvent.ACTION_DOWN:
                if (event.getSource() == InputDevice.SOURCE_TOUCHSCREEN) {
                    mPrivateFlags3 |= PFLAG3_FINGER_DOWN;
                }
                mHasPerformedLongPress = false;

                if (!clickable) {
                    checkForLongClick(0, x, y);
                    break;
                }

                if (performButtonActionOnTouchDown(event)) {
                    break;
                }

                // Walk up the hierarchy to determine if we're inside a scrolling container.
                boolean isInScrollingContainer = isInScrollingContainer();

                // For views inside a scrolling container, delay the pressed feedback for
                // a short period in case this is a scroll.
                if (isInScrollingContainer) {
                    mPrivateFlags |= PFLAG_PREPRESSED;
                    if (mPendingCheckForTap == null) {
                        mPendingCheckForTap = new CheckForTap();
                    }
                    mPendingCheckForTap.x = event.getX();
                    mPendingCheckForTap.y = event.getY();
                    postDelayed(mPendingCheckForTap, ViewConfiguration.getTapTimeout());
                } else {
                    // Not inside a scrolling container, so show the feedback right away
                    setPressed(true, x, y);
                    checkForLongClick(0, x, y);
                }
                break;

            case MotionEvent.ACTION_CANCEL:
                if (clickable) {
                    setPressed(false);
                }
                removeTapCallback();
                removeLongPressCallback();
                mInContextButtonPress = false;
                mHasPerformedLongPress = false;
                mIgnoreNextUpEvent = false;
                mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                break;

            case MotionEvent.ACTION_MOVE:
                if (clickable) {
                    drawableHotspotChanged(x, y);
                }

                // Be lenient about moving outside of buttons
                if (!pointInView(x, y, mTouchSlop)) {
                    // Outside button
                    // Remove any future long press/tap checks
                    removeTapCallback();
                    removeLongPressCallback();
                    if ((mPrivateFlags & PFLAG_PRESSED) != 0) {
                        setPressed(false);
                    }
                    mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                }
                break;
            }
      	return true;
    }
  	return false;
}
```

事件分发的一些总结:

1. `ACTION_DOWN` 是一个**特殊**的事件. 如果`View`只消耗了`ACTION_DOWN`事件(**返回 true**), 那么序列里接下来的事件全都交给该 `View` 来消耗.

   如果`View`没有消耗掉接下来比如`ACTION_MOVE`, `ACTION_UP`之类的事件(**返回`false`**), 那这些事件也不会回退给上一层父`ViewGroup`, 这些事件便会消失

2. 如果某个`View`没有消耗掉`ACTION_DOWN`事件(返回了`false`), 那么同一个序列中的其他事件就不会再交给这个`View`了. 所有的事件包括第一个`ACTION_DOWN`都会被一层一层回退, 如果一直没有`View/ViewGroup`消耗掉, 最终会回退到`Activity`. 但在这一层层中, 我们可以检测到第一次的`ACTION_DOWN`调用, 然后决定是否要消耗事件序列. 原因同 **1**

> 一种特殊情况的举例: 
> 正常情况下, 一个事件序列只能被一个 `View` 拦截消耗, 但如果最后接收事件的 `View` 是不可`clickable`(包括单击, 长按), 那这个 `View` 只能在 `onTouch` (如果调用`View#setOnTouchListener`设置了的话)捕获到, 然后会把这个序列事件(包括 `ACTION_DOWN`)回退给父 `ViewGroup`, 这个也证实第 1 点

3. `View` 没有 `onInterceptTouchEvent` 方法的, 一但有事件传给它, 在没有设置`setTouchEventListener` 或者该方法里的 `onTouch` 返回 `false` 时, 会调用 `onTouchEvent` 方法
4. `view`如果不是`clickable`的, 默认情况下是不能消耗事件的, 非`clickable`的`view`可以设置`setTouchEventListener`来返回`true`截断被消耗事件
5. `View` 的 `enable` 属性并不影响 `onTouchEvent` 的默认返回值(`true`), 只有`clickable`才是
6. `onClick` 调用发生的前提是 `view` 是 `clickable`, 并且在它的`View#onTouchEvent` 消耗了 `ACTION_DOWN` 和 `ACTION_UP` 事件, 如果这其中一个被 `setTouchEventListener` 拦截消耗了, `click` 事件不会被调用 
7. `ViewGroup#requestDisallowInterceptTouchEvent`可以请求不拦截`ACTION_DOWN`以外的事件



**Reference**:

1. [http://blog.csdn.net/yanbober/article/details/50419117](http://blog.csdn.net/yanbober/article/details/50419117)
2. [https://juejin.im/entry/571a591a2e958a006be9f473](https://juejin.im/entry/571a591a2e958a006be9f473)
3. [http://blog.csdn.net/carson_ho/article/details/54136311](http://blog.csdn.net/carson_ho/article/details/54136311)
4. <<Android开发艺术探索>>