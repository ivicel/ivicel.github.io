title: Android硬盘缓存DiskLrucCache
date: 2018-04-04
tags: 缓存, 磁盘缓存, lru, cache, disk cache



### 1. DiskLruCache 的使用

DiskLruCache 并不属于 Android 源码, 只是官方推荐的一种实现方式, 可以在 [这里](https://android.googlesource.com/platform/libcore/+/jb-mr2-release/luni/src/main/java/libcore/io/StrictLineReader.java) 找到源码, 这个源码使用了其他几个自定义类里的方法, 比如读行, 出错打印. Android Developer Sample 里关于 bitmap 的加载使用到了这个类来做缓存, 可直接使用, 可以在 [这里](https://developer.android.com/samples/DisplayingBitmaps/src/com.example.android.displayingbitmaps/util/DiskLruCache.html) 找到源码. 另外一个 [GitHub 备份地址](https://gist.github.com/ivicel/f98f9ba4420c9d2c5274f151b625f677)

> Android Developer Sample 里的源码没有有效的初始化 redundantOpCount, 而是为 0. 这导致如果不断退出重进应用, 很难达到封顶的 2000 行, 即使 journal 已经超出 2000 行. 
>
> GitHub 上已经添加

一般来说我们都会把磁盘放到 sdcard 上, 也就是 `/sdcard/Android/data/app_package_name/cache` 里, 在 **SDK 19** 之前, 外部存储需要声明权限 `WRITE_EXTERNAL_STORAGE`. 

在使用外部存储之前, 还有一样需要注意的是**判断是否存在外部存储**. 

```java
private File getCacheDirectoryFile(Context context, String dirName) {
    File cacheFile;
	if (!Environment.isExternalStorageRemovable ||
        Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState())) {
        // 外部 cache
    	cacheFile = context.getExternalCacheDir();
    } else {
        // 内部 cache
        cacheFile = context.getCacheDir();
    }
    return new File(cacheFile, dirName);
}
```

> DiskLruCache 的缓存目录里不要跟别的缓存相互混合, 以免导致缓存出错

DiskLruCache 构造方法是 `private`, 提供了一个 `DiskLruCache#open()` 方法来获得一个新的对象.

```java
// @param directory 缓存目录
// @param appVersion 版本号, 当版本号发生改变时, 缓存会被清空重建
// @param valueCount 每个节点对应该对应的数据个数, 一般传 1, 一个节点一个数据
// @param maxSize 缓存大小
public static open(File directory, int appVersion, int valueCount, long maxSize);

// 80M 缓存
DiskLruCache lruCache = DiskLruCache.open(getCacheDirectoryFile(context, "images",
		1, 1, 80 * 1024 * 1024);
```

向缓存中写入数据, 由 `DiskLruCache.Editor` 类负责. 使用 `DiskLruCache#edit()` 方法获得一个 `DiskLruCache.Editor` 对象, 便可以打开文件输入和输出流来进行读写. 这里的 `newInputStream()` 只能读到最后一次 `commit`

```java
// 由 key 值获得 Editor 对象, key 值一般也使用 url 的 MD5 值
DiskLruCache.Editor editor = lruCache.edit(key);
// 获得输出流, 参数是数据的数组下标, 指的是在 open 时传入的 valueCount 的值
// 这个值为一个 node 节点以数组的形式来存储多少个数据, 只存一个数据, 其下标为 0
OutputStream out = editor.newOutputStream(0);
// 将 bitmap 压缩成 png 写入到流中, 然后将写入结果记到日志中
if (bitmap.compress(Bitmap.CompressFormat.PNG, 50, out)) {
    editor.commit();
} else {
    editor.abort();
}
```

通过 `DiskLruCache#get()` 方法可以得到一个 `DiskLruCache.Snapshot` 对象, 通过这个对象可以得到缓存文件的输入流

```java
// 根据 key 找到对应的缓存文件
DiskLruCache.Snapshot snapShot = lruCache.get(key);
InputStream in = snapShot.getInputStream(0);
// InputStream 是一种有序的流, 第一次读完后指针便指向流末尾. 用文件描述符即可, 或者重置指针位置
FileDescriptor fd = in.getFD();
// 根据需要的宽高进行压缩
bitmap = loadSpecifyImage(fd, destWidth, destHeight);
```



### 2. DiskLruCache 源码解析

#### 2.1 头部

DiskLruCache 的缓存记录最主要是对其日志文件 journal 进行操作, 一但 journal 文件遭到破坏, 缓存被会被重建. 其格式说明如下:

> ```
> libcore.io.DiskLruCache
> 1
> 1
> 2
>
> DIRTY 335c4c6028171cfddfbaae1a9c313c52
> CLEAN 335c4c6028171cfddfbaae1a9c313c52 3934 2342
> REMOVE 335c4c6028171cfddfbaae1a9c313c52
> DIRTY 1ab96a171faeeee38496d8b330771a7a
> CLEAN 1ab96a171faeeee38496d8b330771a7a 1600 234
> READ 1ab96a171faeeee38496d8b330771a7a
> ```

* 头部, 每一次打开(`DiskLruCache#open`)时都会验证头部是否相符, 如果存在 **journal** 但不相符的, 缓存被清空然后重建. 不存在 **journal** 的, 重建缓存:
  * 第一行是文件标识 `MAGIC`, 默认为 `libcore.io.DiskLruCache`
  * 第二行是 DiskLruCache 类的版本号(`CACHE_VERSION`), 默认是 `1`
  * 第三行是传入的 App 版本号(`APP_VERSION`), 当应用版本号变动时缓存被清空. 要想在应用变更时不清空缓存传入一个**固定值**便可
  * 第四行是 `valueCount`, 代表的是一个 `Node` 结点对应的是几个数据节点. 上面的是 **两** 个
  * 第五行是一个空行分隔行
* 主体记录, 格式为 `status key value[0].length….value[N - 1].length`, 每列值以**空格**分隔
  * `status` 的值有:
    * `DIRTRY` 脏数据, 代表对这条数据进行操作, 每一行 `DIRTY` 后都应该跟着一条 `CLEAN` 或者 `REMOVE`, 代表对数据的操作结束. 如果没有则这条数据为无效数据, 将被删除
    * `CLEAN` 代表这条数据已经写入到磁盘中, 可以进行读写
    * `REMOVE` 代表这条数据已经被删除
    * `READ` 代表读取一条数据
  * `status` 后面跟着 `key`, `CLEAN` 操作后面跟着节点内每条数据的大小, 单位为 `byte`, 上面例子每个节点有两条. 这些**数据的合**代表当前缓存使用的大小


#### 2.2 缓存文件的内部摘要类 Entry

与 LruCache 类似, DiskLruCache 也是一个最近访问最多算法, 其类内部也一样持一个 `LinkedHashMap` 对象 `lruEntries` 来记录其数据被访问记录, 结构为 `<String, DiskLruCache#Entry>`, `key` 是我们传入的, `Entry` 对象为内部私有类, 记录在磁盘上名为 `key` 的文件的一些信息. 比如可读, 可写, 对应 `key` 等

```java
// DiskLruCache#Entry
private final class Entry {
    // 对应的 key
    private final String key;
    // 节点数据的字节数
    private final long[] lengths;
    // 当一条数据有 CLEAN, 即被写到磁盘里时, 为 true
    private boolean readable;
    // The ongoing edit or null if this entry is not being edited.
    private Editor currentEditor;
    // The sequence number of the most recently committed edit to this entry.
    private long sequenceNumber;

    /* ... */

    // 一个 node 对应多个数据时, 是以 key.i 的格式为名字来保存文件
    public File getCleanFile(int i) {
        return new File(directory, key + "." + i);
    }

    public File getDirtyFile(int i) {
        return new File(directory, key + "." + i + ".tmp");
    }
}
```

#### 2.3 打开缓存

DiskLruCache 的构造方法是 `private` 的, 通过静态方法 `DiskLruCache#open()` 来创建一个缓存对象. 构造方法只是简单的保存了一些属性值. 而 `open()` 方法里对 journal 文件进行了判断和验证

创建缓存方法

```java
// DiskLruCache#open()
public static DiskLruCache open(File directory, int appVersion, int valueCount, 
		long maxSize) throws IOException {
 	/* ... */   
    // prefer to pick up where we left off
    DiskLruCache cache = new DiskLruCache(directory, appVersion, valueCount, 
			maxSize);
    // 如果已经存在了 journal 文件, 读取头部进行对比
    // 对比失败会删除该缓存目录, 然后再重建一个缓存目录
    if (cache.journalFile.exists()) {
        try {
            // 验证头部, 读取日志中的每一行
            // 跳过 REMOVE 记录, 只保存 READ, DIRTY, CLEAN. 到 LinkedHashMap 中
            // CLEAN 设置 readable = true, 节点每个数据的大小到 lenghts 数组
            // DIRTY 设置 currentEditor = new Editor(entry)
            // READ 不作改变
            cache.readJournal();
            // 
            cache.processJournal();
            cache.journalWriter = new BufferedWriter(
                	new FileWriter(cache.journalFile, true), IO_BUFFER_SIZE);
            return cache;
        } catch (IOException journalIsCorrupt) {
            cache.delete();
        }
    }

    // create a new empty cache
    directory.mkdirs();
    cache = new DiskLruCache(directory, appVersion, valueCount, maxSize);
    cache.rebuildJournal();
    return cache;
}
```

`open()` 里即使传入的目录不存在, DiskLruCache 也是会帮我们重建一个缓存目录的. 

```java
// DiskLruCache#rebuildJournal()
private synchronized void rebuildJournal() throws IOException {
    if (journalWriter != null) {
        journalWriter.close();
    }

    // 使用临时 journal 文件来重建缓存, 重建完成后再更名为正式的 journal 文件名
    // 按格式写入头部
    /* ... */

    // 将内存中已经读取的缓存记录写到文件里
    for (Entry entry : lruEntries.values()) {
        if (entry.currentEditor != null) {
            writer.write(DIRTY + ' ' + entry.key + '\n');
        } else {
            writer.write(CLEAN + ' ' + entry.key + entry.getLengths() + '\n');
        }
    }
	// 关闭文件, 重命名, 将 journalWriter 指向新文件
    writer.close();
    journalFileTmp.renameTo(journalFile);
    journalWriter = new BufferedWriter(new FileWriter(journalFile, true), IO_BUFFER_SIZE);
}
```

`readJournal()`, `readJournalLine()`, `processJournal()` 这三个方法是重要的操作 journal 文件的方法. `readJournal()` 处理好正确的头部匹配, 然后调用  `readJournalLine()` 来读取每一行主体内容. 处理的步骤为: 
1. 每读到一个 REMOVE 就删除 `lruEntries` 里对应 key 的 entry
2. 如果这一行不为 REMOVE, 并且其不在 `lruEntries` 里, 就将为其创建一个 entry 加入到链表中
3. 如果这一行为 CLEAN, 那表示这条数据已确保写到磁盘了, 设置为 `readable = true`, `currentEditor = null`, 并将该节点的数据大小进行保存
4. 如果这一行为 DIRTY, 表示这条数据有过编辑(`DiskLruCache#.edit()`), 为其创建一个编辑器
5. 如果这一行为 READ, 已经在 2 里处理过了

这样就处理了所有的标记符. 在 `processJournal()` 方法里, 删除掉 DIRTY 记录. 因为一条 DIRTY 只对应一条 CLEAN 或 REMOVE, REMOVE 对应的 DIRTY 我们已经在第一次读到时已经删除过. 另外在每次读到 CLEAN 时, 我们都会把其对应的 DIRTY 的 `currentEditor` 设置为 `null`, 所以只要查找 `currentEditor = null` 记录便可

```java
// DiskLruCache#readJournal()
// 这个方法主要是验证头部正确后, 把日志时的每条记录都读到 lruEntries 中
private void readJournal() throws IOException {
    InputStream in = new BufferedInputStream(new FileInputStream(journalFile), IO_BUFFER_SIZE);
    try {
        // 验证头部, 每次读一行, 分别与传入的值对比
        /* ... */
        
		// 如果头部无误, 将除 REMOVE 之外的记录读到 lruEntries 中
        int lineCount = 0;
        while (true) {
            try {
                readJournalLine(readAsciiLine(in));
                lineCount++;
            } catch (EOFException endOfJournal) {
                break;
            }
        }
        redundantOpCount = lineCount - lruEnties.size();
    } finally {
        closeQuietly(in);
    }
}


// DiskLruCache#readJournalLine()
private void readJournalLine(String line) throws IOException {
    String[] parts = line.split(" ");
    if (parts.length < 2) {
        throw new IOException("unexpected journal line: " + line);
    }
	// 当读到 REMOVE 表示我们要删除该条对应的 DIRTY 记录
    String key = parts[1];
    if (parts[0].equals(REMOVE) && parts.length == 2) {
        lruEntries.remove(key);
        return;
    }
	// 过滤掉 REMOVE 匹配的一次 DIRTY 记录后, 剩下的记录都会读到 lruEntries
    Entry entry = lruEntries.get(key);
    if (entry == null) {
        entry = new Entry(key);
        lruEntries.put(key, entry);
    }
	
    if (parts[0].equals(CLEAN) && parts.length == 2 + valueCount) {
        // CLEAN 表示保存了文件, 是可读的
        entry.readable = true;
        entry.currentEditor = null;
        // 设置其节点有多少份数据, copyOfRange 同 Arrays.copyOfRange
        entry.setLengths(copyOfRange(parts, 2, parts.length));
    } else if (parts[0].equals(DIRTY) && parts.length == 2) {
        // 为 DIRTY 记录设置一个可写对象
        entry.currentEditor = new Editor(entry);
    } else if (parts[0].equals(READ) && parts.length == 2) {
        // this work was already done by calling lruEntries.get()
    } else {
        throw new IOException("unexpected journal line: " + line);
    }
}


// DiskLruCache#processJournal()
// 再把日志的数据都读到 lruEntries 后, 删除其中的 DIRTY 数据
// 因为每一条 DIRTY 至少匹配 REMOVE
private void processJournal() throws IOException {
    deleteIfExists(journalFileTmp);
    for (Iterator<Entry> i = lruEntries.values().iterator(); i.hasNext(); ) {
        Entry entry = i.next();
        if (entry.currentEditor == null) {
            // 删除到记录不正确的 DIRTY 后, 才计算现在使用了多少容量
            for (int t = 0; t < valueCount; t++) {
                size += entry.lengths[t];
            }
        } else {
            // 删除 DIRTY 记录
            entry.currentEditor = null;
            for (int t = 0; t < valueCount; t++) {
                deleteIfExists(entry.getCleanFile(t));
                deleteIfExists(entry.getDirtyFile(t));
            }
            i.remove();
        }
    }
}
```

#### 2.4 写入缓存

在将日志记录读到 `lruEntries` 后, 便可以进行读写操作. 写操作是获得一个 `DiskLruCache#Editor` 对象.

```java
private synchronized Editor edit(String key, long expectedSequenceNumber) throws IOException {
    // 检测文件没有关闭和 key 的有效性, 不能包含空格和换行: ' ', '\r', '\n'
    checkNotClosed();
    validateKey(key);
    // lruEntries 中取出该记录, 如果不为 null, 说明不是新记录; 并且如果其
    // 保存了 currentEditor 的话说明有其他线程在编辑, 因为我们会把完成的 DIRTY 记录
    // 从 lruEntries 中删除掉
    Entry entry = lruEntries.get(key);
    if (expectedSequenceNumber != ANY_SEQUENCE_NUMBER
            && (entry == null || entry.sequenceNumber != expectedSequenceNumber)) {
        return null; // snapshot is stale
    }
  	// 这里要注意如果我们获取了一次 Editor 对象, 再次获取前没有 commit/abort 操作则返回 null
    if (entry == null) {
        entry = new Entry(key);
        lruEntries.put(key, entry);
    } else if (entry.currentEditor != null) {
        return null; // another edit is in progress
    }
	// 获取一个新的编辑状态
    Editor editor = new Editor(entry);
    entry.currentEditor = editor;

    // 写入 DIRTY 状态
    journalWriter.write(DIRTY + ' ' + key + '\n');
    journalWriter.flush();
    return editor;
}
```

在拿到 `Editor` 对象之后, 便可以获得输出流, 将图片之类写到磁盘作缓存. 

```java
public final class Editor {
    private final Entry entry;
    private boolean hasErrors;

    // 返回的是一个 FilterOutputStream, 如果出错就把标志位 hasErrors 设为 true
    // 在写完后 commit 时检查标志位, 有错误会放弃该缓存
    public OutputStream newOutputStream(int index) throws IOException {
        synchronized (DiskLruCache.this) {
            if (entry.currentEditor != this) {
                throw new IllegalStateException();
            }
            // FileOutputStream 会帮我们自动创建文件
            return new FaultHidingOutputStream(
                	new FileOutputStream(entry.getDirtyFile(index)));
        }
    }

    /* ... */
}
```

调用 `DiskLruCache.Editor#commit()` 时会调用 `DiskLruCache#completeEdit()` 完成最终编辑

```java
private synchronized void completeEdit(Editor editor, boolean success) 
    	throws IOException {
    	// 检查 DIRTY 文件是否创建了
        if (success && !entry.readable) {
            for (int i = 0; i < valueCount; i++) {
                if (!entry.getDirtyFile(i).exists()) {
                    editor.abort();
                    throw new IllegalStateException("edit didn't create file " + i);
                }
            }
        }
        // 重命名文件, 减去老的缓存大小
        for (int i = 0; i < valueCount; i++) {
            File dirty = entry.getDirtyFile(i);
            if (success) {
                if (dirty.exists()) {
                    File clean = entry.getCleanFile(i);
                    dirty.renameTo(clean);
                    long oldLength = entry.lengths[i];
                    long newLength = clean.length();
                    entry.lengths[i] = newLength;
                    size = size - oldLength + newLength;
                }
            } else {
                deleteIfExists(dirty);
            }
        }
        // 操作行数增加 1
        redundantOpCount++;
    	// 操作完成时重置为 null
        entry.currentEditor = null;
        if (entry.readable | success) {
            entry.readable = true;
            journalWriter.write(CLEAN + ' ' + entry.key + entry.getLengths() + '\n');
            if (success) {
                // sequenceNumber 用来记录该 entry 是否过期, 在获取 Shapshot 时会与
                // entry.sequenceNumber 对比, 如果不相等则是过期的
                entry.sequenceNumber = nextSequenceNumber++;
            }
        } else {
            lruEntries.remove(entry.key);
            journalWriter.write(REMOVE + ' ' + entry.key + '\n');
        }
        // 判断是否超出设定的缓存容量, 是否操作行数记录大于 2000, 
    	// 或者 redundantOpCount > lruEntries.size()
    	// 以便来决定是否在释放一些缓存
        if (size > maxSize || journalRebuildRequired()) {
            executorService.submit(cleanupCallable);
        }
    }
```

#### 2.5 读取缓存

通过 `DiskLruCache#get()` 获得一个 `Snapshot` 缓存对象. 该对象主要是 `InputStream` 的再封装

```java
// DiskLruCache#get
public synchronized Snapshot  (String key) throws IOException {
    // 检查文件是否打开, key 是否正确
    /* ... */

    // 一次性打开所有的数据以保证一个 key 即使对应多个数据也只有一个 snapshot
    InputStream[] ins = new InputStream[valueCount];
    try {
        for (int i = 0; i < valueCount; i++) {
            ins[i] = new FileInputStream(entry.getCleanFile(i));
        }
    } catch (FileNotFoundException e) {
        // a file must have been deleted manually!
        return null;
    }
    // 记录操作数, 写入操作记录, 之后要再检查操作记录是否超出设定
    redundantOpCount++;
    journalWriter.append(READ + ' ' + key + '\n');
    if (journalRebuildRequired()) {
        executorService.submit(cleanupCallable);
    }

    return new Snapshot(key, entry.sequenceNumber, ins);
}
```

#### 2.6 删除缓存

每次读, 写, 删除缓存后, 都要再次判断操作记录或者缓存大小已经超出设置的值. 删除操作主要是由一个

```java
// 调用 remove
// DiskLruCache#remove
public synchronized boolean remove(String key) throws IOException {
    checkNotClosed();
    validateKey(key);
    Entry entry = lruEntries.get(key);
    if (entry == null || entry.currentEditor != null) {
        return false;
    }
	// 删除对应 key 的所有文件
    for (int i = 0; i < valueCount; i++) {
        File file = entry.getCleanFile(i);
        if (!file.delete()) {
            throw new IOException("failed to delete " + file);
        }
        size -= entry.lengths[i];
        entry.lengths[i] = 0;
    }
	// 是否要重建 journal 文件
    redundantOpCount++;
    journalWriter.append(REMOVE + ' ' + key + '\n');
    lruEntries.remove(key);

    if (journalRebuildRequired()) {
        executorService.submit(cleanupCallable);
    }

    return true;
}

private final ExecutorService executorService = new ThreadPoolExecutor(0, 1, 60L,
		TimeUnit.SECONDS, new LinkBlockingQueue<Runnable>());
private final Callable<Void> cleanupCallable = new Callable<>() {
  	@Override
    public Void call() throw Exception {
     	synchronized (DiskLruCache.this) {
         	if (journalWriter == null) {
                return null;
            }
            trimeToSize();
            if (journalRebuildRequired()) {
                rebuildJournal();
                redundantOpCount = 0;
            }
            return null;
        }
    }
};

private void trimToSize() throws IOException {
    // 循环迭代删除超出的空间
 	while (size > maxSize) {
        final Map.Entry<String, Entry> toEvict = 
            lruEntries.entrySet().iterator.next();
        remove(toEvict.getKey());
    }
}
```






### Reference

1. <<Android开发艺术探索>>
2. [https://blog.csdn.net/shakespeare001/article/details/51695358](https://blog.csdn.net/shakespeare001/article/details/51695358)
3. [https://www.jianshu.com/p/b282140acc20](https://www.jianshu.com/p/b282140acc20)
4. [http://nirvanawoody.com/2016/05/05/Android-DiskLruCache](http://nirvanawoody.com/2016/05/05/Android-DiskLruCache)