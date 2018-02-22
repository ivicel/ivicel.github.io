Title: Android加载缩略图片防止OOM
Date: 2018-02-22
Tags: andorid图片加载



依据想需要的大小生成`bitmap`

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
      	/* inSampleSize指的是将原图片的按 1/inSampleSize 缩放, 所以取比例较大的值 */
      	inSampleSize = Math.round(widhtScale > heightScale ? widthScale : heightScale);
    }
  	options.inJustDecodeBounds = false;
  	options.inSampleSize = inSampleSize;
  	return BitmapFactory.decodeFile(imagePath, options);
}
```

