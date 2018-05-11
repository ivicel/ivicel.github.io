title: CircleImageView实现解析
date: 2018-04-28
tags: CircleImageView, 源码解析, 实现



### 1. CircleImageView 的实现

#### 1.1 自定义的属性

CircleImageView 一共自定义的 5 个自定义属性

1. `civ_border_width` 边框的大小
2. `civ_border_color` 边框的颜色
3. `civ_border_overlay` 边框覆盖
4. `civ_fill_color` 图片背景填充, 已弃用, 使用 `civ_circle_background_color` 替代

#### 1.2 流程

CircleImageView 是继承自系统控件 `android.widget.ImageView`, 而不是 support 里的兼容控件 `android.support.v7.widget.AppCompatImageView`, 作者的理由是为了使用控件更加简洁, 这样不必在包内依赖 android support v7 包, 减小包的大小. 如果有版本兼容问题的话, 我们可以自己按需求改成继承自 v7 包.

> CircleImageView 里有两个重要的标志位 `mReady`, `mSetupPending`. 用来控制解析自定义属性, 和图片来源以及 view 大小的测量. 为什么要使用两个标志位并相互依赖? 这是由于 ImageView 可能通过 xml 和 java 两种方法来设置图片来源, 这两种方法调用的时机也是不同. 另外我们需要确保先要解析我们自定义的值才好计算出边框大小, 颜色等, 还有 view 的大小要到 onMeasure 时才能确定, 所以圆半径大小的要到那时才能确定

我们都知道, xml 的 inflate 使用的是控件里的第二个构造方法, 即 `public CircleImageView(Context context, AttributeSet attrs)`, 然后这里调用了 `public CircleImageView(Context context, AttributeSet attrs, int defStyle)`.

在第三个构造调用了父类 `ImageView` 里对应的构造方法, 这里要注意的是, 父类里会解析我们所写的 xml 文件, 然后如果我们写了图片文件来源 `android:src`, 这里就会调用了 `ImageView#setDrawable` 来设置图片文件来源.

然后我们看到 CircleImageView 源码里面设置图片的 setXXX 方法都已经被重写了, 都只增加了一行 `initializeBitmap()` 来初始化图片 mBitmap 来源.

```java
private void initializeBitmap() {
    // 通过这个标志可以设定我们是否需要把图片变形为圆形或者不改变
    // 如果设定了 onDraw 那就按 ImageView 来绘画
    if (mDisableCircularTransformation) {
        mBitmap = null;
    } else {
        // 获取图片
        mBitmap = getBitmapFromDrawable(getDrawable());
    }
    setup();
}

private void setup() {
    // 第一次 mReady 初始为 false, 所以总是直接返回, 回到构造方法里解析自定义属性
    if (!mReady) {
        mSetupPending = true;
        return;
    }
    // 这一步判断也是很重要的, 因为图片的设置可能是在 xml 也可能是在 java 中 setXXX 方法
    // 所以当完成调用构造方法后, 再次调用 setup 时并没有测量好 view 的大小, 这里就会直接返回
    if (getWidth() == 0 && getHeight() == 0) {
        return;
    }
    
    /* .... */
}
```

来看两种情况:

1. 通过 xml 设置图片来源. 
	
`setImageDrawable()` -> `initializeBitmap()` -> `setup()`, 遇到 `mReady == false` 返回 -> 构造方法里解析自定义属性, 然后 `init()` -> 这时 `mSetupPending == true`, 再次调用 `setup()`, 但此时 view 的大小还没测量好, `getWidth() == 0`, `getHeight() == 0` 直接返回. 

当 view 测量完成后调用 `onSizeChanged()` -> 再次 `setup`, 这时一切就绪可以测量圆的半径大小, 位置等种种

2. 通过 java 代码来设置图片来源.

重写 `setImageXXXX()` 方法, 里面都调用了 `initializeBitmap()`. 然后跟上面的一样, 只不过这时候 `mReady` 已经是 `true`, 因为在 `init()` 里已经设置了, 并且此时我们已经完成了对 view 的测量, 这样在 `setup()` 里就直接测量圆的半径等等所需的值

```java
private void init() {
    super.setScaleType(SCALE_TYPE);
    mReady = true;

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
        setOutlineProvider(new OutlineProvider());
    }
	// 如果已经在 xml 设置了图片, 就会直接设置图片的大小等
    if (mSetupPending) {
        setup();
        mSetupPending = false;
    }
}
```

来看如何获得 bitmap.

```java
private Bitmap getBitmapFromDrawable(Drawable drawable) {
    if (drawable == null) {
        return null;
    }
	// 如果是 BitmapDrawable 对象, 直接使用 BitmapDrawable#getBitmap() 获得
    if (drawable instanceof BitmapDrawable) {
        return ((BitmapDrawable) drawable).getBitmap();
    }

    try {
        Bitmap bitmap;
		// 如果是 ColorDrawable 对象, 因为填充颜色没有所谓的大小, 是根据要填充的 view 来确定大小的. 
        // 所以给一个初始的大小来生成 bitmap, 到时把这个 bitmap 拉伸便可
        if (drawable instanceof ColorDrawable) {
            bitmap = Bitmap.createBitmap(COLORDRAWABLE_DIMENSION, COLORDRAWABLE_DIMENSION, BITMAP_CONFIG);
        } else {
            // 其余情况下由传入的 drawable 大小来确定生成新的 bitmap
            bitmap = Bitmap.createBitmap(drawable.getIntrinsicWidth(), drawable.getIntrinsicHeight(), BITMAP_CONFIG);
        }
        Canvas canvas = new Canvas(bitmap);
        drawable.setBounds(0, 0, canvas.getWidth(), canvas.getHeight());
        drawable.draw(canvas);
        return bitmap;
    } catch (Exception e) {
        e.printStackTrace();
        return null;
    }
}
```

回过来看最重要的 setup 方法

```java
private void setup() {
    if (!mReady) {
        mSetupPending = true;
        return;
    }

    if (getWidth() == 0 && getHeight() == 0) {
        return;
    }
	// 设置为不要变形为圆形时的情况, 会执行这个
    if (mBitmap == null) {
        invalidate();
        return;
    }
	// 设置着色器
    mBitmapShader = new BitmapShader(mBitmap, Shader.TileMode.CLAMP,
			Shader.TileMode.CLAMP);
    // 图片画笔, 反锯齿, 着色器
    mBitmapPaint.setAntiAlias(true);
    mBitmapPaint.setShader(mBitmapShader);
	// 边框画笔样式
    mBorderPaint.setStyle(Paint.Style.STROKE);
    mBorderPaint.setAntiAlias(true);
    mBorderPaint.setColor(mBorderColor);
    mBorderPaint.setStrokeWidth(mBorderWidth);
	// 背景画笔样式
    mCircleBackgroundPaint.setStyle(Paint.Style.FILL);
    mCircleBackgroundPaint.setAntiAlias(true);
    mCircleBackgroundPaint.setColor(mCircleBackgroundColor);
	// 图片宽高
    mBitmapHeight = mBitmap.getHeight();
    mBitmapWidth = mBitmap.getWidth();
	// 计算圆形的外切矩形大小
    mBorderRect.set(calculateBounds());
    // 计算边框的半径, 我们在 xml 中设置的是边框大小 * 2, 这里要除以 2
    // 因为在画圆时, Paint#setStrokeWidth 的参数就是圆边框线的两倍
    mBorderRadius = Math.min((mBorderRect.height() - mBorderWidth) / 2.0f,
			(mBorderRect.width() - mBorderWidth) / 2.0f);
    mDrawableRect.set(mBorderRect);
    // overlay 为 true 时, 向内缩小 1px
    if (!mBorderOverlay && mBorderWidth > 0) {
        mDrawableRect.inset(mBorderWidth - 1.0f, mBorderWidth - 1.0f);
    }
    // 图形圆的半径大小, 可以看到取这个大小时, 边框是画在图像上的
    mDrawableRadius = Math.min(mDrawableRect.height() / 2.0f, mDrawableRect.width() / 2.0f);
	// 过滤颜色, 只在 java 代码中设置调用
    applyColorFilter();
    updateShaderMatrix();
    invalidate();
}

 private RectF calculateBounds() {
    // 注意先要减去上下左右的 padding 才是 view 真正的内容区大小
    int availableWidth  = getWidth() - getPaddingLeft() - getPaddingRight();
    int availableHeight = getHeight() - getPaddingTop() - getPaddingBottom();
	// 取长宽里的最小值来作一个内切圆, 该值就是边框圆的直径
    int sideLength = Math.min(availableWidth, availableHeight);
	// 以左, 上的 padding 为准来定位圆
    // 如果长, 高很大, 那么 paddingRight, paddingBottom 可能不会产生什么影响 
    float left = getPaddingLeft() + (availableWidth - sideLength) / 2f;
    float top = getPaddingTop() + (availableHeight - sideLength) / 2f;
	// 将在这个矩形内作一个内切圆
    return new RectF(left, top, left + sideLength, top + sideLength);
}

private void updateShaderMatrix() {
    float scale;
    float dx = 0;
    float dy = 0;
    mShaderMatrix.set(null);
    // 我们已经计算好一个矩形, 我们需要知道图片比预定矩形大还是小, 以便作缩放
    // 下面是 mDrawableRect.height() / mBitmapHeight > 
    // mDrawableRect.width() / mBitmapWidth 的变形
    // 因为图片有放大或缩小, 缩放中心为原点, 所以图片要进行移动
    if (mBitmapWidth * mDrawableRect.height() > 
	        mDrawableRect.width() * mBitmapHeight) {
        // 按高进行缩放时, 要在 x 轴平移
        scale = mDrawableRect.height() / (float) mBitmapHeight;
        dx = (mDrawableRect.width() - mBitmapWidth * scale) * 0.5f;
    } else {
        // 按宽进行缩放时, 要在 y 轴平移
        scale = mDrawableRect.width() / (float) mBitmapWidth;
        dy = (mDrawableRect.height() - mBitmapHeight * scale) * 0.5f;
    }

    mShaderMatrix.setScale(scale, scale);
    mShaderMatrix.postTranslate((int) (dx + 0.5f) + mDrawableRect.left, (int) (dy + 0.5f) + mDrawableRect.top);

    mBitmapShader.setLocalMatrix(mShaderMatrix);
}

protected void onDraw(Canvas canvas) {
    // 禁用变形
    if (mDisableCircularTransformation) {
        super.onDraw(canvas);
        return;
    }
	// 没有获得图片源
    if (mBitmap == null) {
        return;
    }
	// 有背景颜色
    if (mCircleBackgroundColor != Color.TRANSPARENT) {
        canvas.drawCircle(mDrawableRect.centerX(), mDrawableRect.centerY(), mDrawableRadius, mCircleBackgroundPaint);
    }
    // 画图片
    canvas.drawCircle(mDrawableRect.centerX(), mDrawableRect.centerY(),
			mDrawableRadius, mBitmapPaint);
    // 画边框
    if (mBorderWidth > 0) {
        canvas.drawCircle(mBorderRect.centerX(), mBorderRect.centerY(), 
				mBorderRadius, mBorderPaint);
    }
}
```



















### Reference

1. [http://www.jcodecraeer.com/a/anzhuokaifa/androidkaifa/2015/0806/3268.html](http://www.jcodecraeer.com/a/anzhuokaifa/androidkaifa/2015/0806/3268.html)
2. [https://juejin.im/entry/593108c4a22b9d0058c08a2c](https://juejin.im/entry/593108c4a22b9d0058c08a2c)
3. [https://github.com/hdodenhof/CircleImageView](https://github.com/hdodenhof/CircleImageView)