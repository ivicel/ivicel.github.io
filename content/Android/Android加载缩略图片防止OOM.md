Title: Android高效加载图片防止OOM
Date: 2018-02-22
Tags: andorid图片加载



想要高效的加载 Bitmap, 最主要的思想就是只加载能显示的尺寸大小. 其通 `BitmapFactory.Options` 里的 `option.inSampleSize` 来设置图片的采样率. 图片的**长**和**宽**都会被设置成 **1/`option.inSampleSize` ** 大小.即当为 1 时, 为原始大小; 当为 2 时, 图片为 `(长 * 1/2) * (宽 * 1/2) * 4`(ARGB8888), 缩小了 4 倍. 即图片会被设置成 `1/option.inSampleSize * 1/option.inSampleSize` 大小.

`inSampleSize` 一般取为 2 的指数, 有些系统会对其向下取整为近似 2 的指数, 但不是所有系统都会这么做. 如果当长和宽的 `inSampleSize` 不一样时, 取较小的值, 这样可以让图片不至于模糊

生成所需大小的 bitmap 的一般步骤:

1. `new` 一个新 `BitmapFactory.Options` 对象, 并将其 `BitmapFactory.Options.inJustDecodeBounds` 设置为 `true`, 这样可以使其解析图片时, 并不会加载图片而只是解读其中信息
2. 获得图片的长和宽, 分别为所期望的长和宽进行对比, 取其中**比值大**的数
3. `BitmapFactory.Options.inJustDecodeBounds` 设置成 `false`, 重新解析出所需图片



<<Android开发权威指南>>依据想需要的大小生成 `bitmap`, 其取的值是较大值, 然后向下取整. 这样能获得更小的分辨率, 占用的内存更小

```java
public Bitmap loadSpecifySizeImage(String imagePath, int destWidth, int destHeight) {
    BitmapFactory.Options options = new BitmapFactory.Options();
  	/* 设置为true后, 在decode时不会真的加载图片而是获取图片信息 */
  	options.inJustDecodeBounds = true;
  	BitmapFactory.decodeFile(imagePath, options);
  	int srcWidth = options.outWidth;
  	int srcHeight = options.outHeight;
  	int inSampleSize = 1;
  	if (srcWidth > destWidth || srcHeight > destHeight) {
        float widthScale = srcWidth / destWidth;
      	float heightScale = srcHeight / destHeight;
      	/* inSampleSize指的是将原图片的长宽都按 1/inSampleSize 缩放, 所以取比例较大的值 */
      	inSampleSize = Math.round(widhtScale > heightScale ? widthScale : heightScale);
    }
  	options.inJustDecodeBounds = false;
  	options.inSampleSize = inSampleSize;
  	return BitmapFactory.decodeFile(imagePath, options);
}
```

Android Develper 官网的示例, 其严格的按 2 的倍数来取值

```java
public Bitmap loadSpecifySizeImage(String imagePath, int destWidth, int destHeight) {
 	BitmapFactory.Options options = new BitmapFactory.Options();
    options.inJustDecodeBounds = true;
    BitmapFactory.decodeFile(imagePath, options);
    int inSampleSize = 1;
    if (options.outWidth > destWidth || options.outHeight > destHeight) {
        // 取一半值, 按 2 的倍数
    	final int halfWidth = options.outWidth / 2;
        final int halfHeight = opitons.outHeight / 2;
        while (halfWidth / inSampleSize >= destWidth &&
               halfHeight / inSampleSize >= destHeight) {
         	inSampleSize *= 2;   
        }
    }
    
    options.inJustDecodeBounds = false;
    otpions.inSampleSize = inSampleSize;
    return BitmapFactory.decodeFile(imagePath, options);
}
```



### Reference

1. <<Android开发艺术>>
2. <<Android开发权威指南>>
3. [https://developer.android.com/topic/performance/graphics/load-bitmap.html](https://developer.android.com/topic/performance/graphics/load-bitmap.html)