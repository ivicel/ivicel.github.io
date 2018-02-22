Title: Anroid FileProvider的使用
Date: 2018-02-22
Tags: android, fileprovider



> `FileProvider` 是在 `v4 support library` 里的, 使用之前要添加 `v4 support library` 
>
> 默认 `v7 support` 继承了 `v4`

1. 在`manifest`中指定分享的文件, 具体的分享目录路径在`res/xml/filepaths`中指定, `android:authorities`为指定的认证, 自行定义, 一般为 `package name` + `fileprovider`, 其他为固定写法

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">
	  <application
        ...>
        
        <provider
        	android:name="android.support.v4.content.FileProvider"
            android:authorities="com.example.myapp.fileprovider"
            android:grantUriPermissions="true"
            android:exported="false">
        	<meta-data
            	android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/filepaths"/>
        </provider>
        
        ...
    </application>
</manifest>
```

2. `res/xml/filepaths`写法

   ```xml
   <paths>
     <files-path path="images" name="my-images"/>
     <cache-path path="..." name="..."/>
     <external-files-path path="...." name="..."/>
     <external-cache-path path="...." name="..."/>
     <external-path path="..." name="...."/>
   </paths>
   ```

   - `file-path`为`Context.getFilesDir()`代表的目录, 内部(**internal**)存储目录`files/`.可能有两个位置, `/data/data/package_name/files`下, 或者`/data/user/../package_name/files`下
   - `cache-path`为`Context.getCacheDir()`代表的内部目录 `cache/`
   - `external-files-path`为外部存储目录`Context#getExternalFilesDir(String)` 和`Context.getExternalFilesDir(null)`这个目录一般在外部存储中的`Android/data/package_name/files`中
   - `external-cache-path`为外部缓存目录`Android/data/package_name/cache`中, 由`Context.getExternalCacheDir()`获得
   - `external-path`为外部存储的根目录`Context.getExternalStorageDirectory()`

   > 如果使用外部目录, 因为存在 `SDCard`可插拔的原因, 最好使用`Environment.getExternalStorageState()`来检测当前外部存储状态, 返回`Environment.MEDIA_MOUNTED`表示存储可用.

`path="path"`

> 代表是指定目录下的子目录, 或者当前目录(使用`.`表示共享当前目录)

`name="name"`

> 代表将共享的目录名称(`path`)在生成`content://uri`时替换成这个值

3. 使用`FileProvider.getUriForFile(Context, String, File)`方法来获取共享的文件`uri`路径

   ```java
   /* 生成 content://com.example.myapp.fileprovider/my_images/default_image.jpg */
   File imagePath = new File(context.getFilesPath(), "images");
   File newFile = new File(imagePath, "default_image.jpg");
   Uri contentUri = FileProvider.getUriForFile(context, "com.example.myapp.fileprovider",
   		newFile);
   ```

   `authorities`参数要和`meta-data`中写的一样, 不然会找不到共享目录, 抛出错误. `getUriForFile`会在设定好的`xml`文件中从上逐行进行匹配, 若匹配不到任何一行, 抛出`IllegalArgumentException`

4. 给`uri`授予权限, 为了兼容**Kitkat**(SDK 19)及以下的Android版本, 一定要对`uri`授予读写权限. 在`Kitkat`以上的版本会自动授予权限.

   - 使用`Context.grantUriPermissioin(package, Uri, mode_flags)`来授权, 比如`Intent.FLAG_GRANT_READ_URI_PERMISSIOIN`和`Intent.FLAG_GRANT_WRITE_URI_PERMISSION`标志位, 在适当的时候使用`Context.revokeUriPermission(Uri, mode_flags)`来去掉授予的权限
   - 或者使用`Intent.setData()`把`uri`放到`intent`中后, 使用`Intent.setFlags()`来设置权限标志位, 建议使用这种授权方式, 这样就不用手动来取消授权了

   ```java
   List<ResolveInfo> resolveActivities = getPackageManager().queryInetntActivities(
   		imageCapture, PackageManager.MATCH_DEFAULT_ONLY);
   /* 为每个activity授权 */
   for (ResolveInfo resolveActivity : resolveActivities) {
       grantUriPermission(resolveActivity.activityInfo.packageName, uri,
   			Intent.FLAG_GRANT_WRITE_PERMISSION);
   }
   ```

   ​


##### Reference:

1. [Android Developer FileProvider](https://developer.android.google.cn/reference/android/support/v4/content/FileProvider.html?hl=zh-cn#getUriForFile(android.content.Context, java.lang.String, java.io.File))
2. [Android Tranning Share a File](https://developer.android.google.cn/training/secure-file-sharing)