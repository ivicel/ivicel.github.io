title: AsyncTask机制分析
date: 2018-04-10
tags: 线程, 线程池, AsyncTask



### 1. AsyncTask 的使用

AsyncTask 为抽象类, 继承该类至少要重写 `doInBackground(Params...params)` 方法. 除了该方法是在**非主程**中执行外, 其他的如 `onPreExecute()` `onProgressUpdate(Progress...progresses)` `onPostExecute(Result result)` `onCancel()` 都是在主线程中执行. 

AsyncTask 另外可以设置三个类型参数, `AsyncTask<Params, Progress, Result>` . 分别指传入  `doInBackground(Param…params)`  的参数数组, `onProgressUpdate(Progress…progress)` 进度更新参数,  从 `doInBackground()` 返回结果, 可在 `onPostExecute(Result result)` 中接收到该结果.

```java
public static DownloadTask extends AsyncTask<String, Integer, Long> {
 	@Override
    protected Long doInBackground(String...urls) {
     	int i = 0;
        for (String url : urls) {
         	Log.d(TAG, "get url: " + url);
            i++;
            publishProgress(i);
        }
        return i;
    }
    
    @Override
    protected void onProgressUpdate(Integer...progress) {
        for (Integer p : progress) {
     		Log.d(TAG, "get progress: " + p);
        }
    }
	
    @Override
    protected void onPostExecute(Long result) {
     	Log.d(TAG, "get result: " + result);    
    }
}

DownloadTask<String, Integer, Long> task = new DownloadTask<>();
task.execute(urls);
```

* 在 **SDK 17(JellyBean_MR1)** 之后新建对象和 `execute()` 方法不必在主线程中调用了, 因为 sHandler 这个静态变量已经在内部使用 Looper.getMainLooper 来初始化了. [查看源码](https://android.googlesource.com/platform/frameworks/base/+/jb-mr1-release/core/java/android/os/AsyncTask.java)
* 不要在重写时直接调用 `onXXXX` 方法
* 一个 AsyncTask 对象只能执行一次 `execute/executeOnExecutor`
* `AsyncTask#execute()` 默认是串行执行, 可以使用 `AsyncTask#executOnExecutor()` 来并行执行任务.



### 2. 源码分析(基于 SDK 27)

当我们创建一个新的 AsyncTask 对象时, 都会走到 `AsyncTask(Looper callbackLooper)` 这个构造方法. 如果没传入 null 或者 main looper 时, 就会默认使用主线程的 looper

#### 2.1 构造方法

```java
public AsyncTask(Looper callbackLooper) {
    // 使用自定义 handler 或者使用默认的 handler, 默认 handler 在主线程中执行
    mHandler = callbackLooper == null || callbackLooper == Looper.getMainLooper()
            ? getMainHandler()
            : new Handler(callbackLooper);
	// 初始化执行参数和返回结果
    /* .... */
}
```

#### 2.2 执行方法

`AsyncTask#execute` 其实也是调用了 `AsyncTask#executeOnExecutor`, 其传入了一个内部实现的串行 `Executor`. 

```java
// AsyncTask#executeOnExecutor
public final AsyncTask<Params, Progress, Result> executeOnExecutor(Executor exec,
            Params... params) {
    	// 判断当前状态, 运行中或已完成的将抛出错误. 这也证明了前面说的每个对象只能调用一次执行
        if (mStatus != Status.PENDING) {
            switch (mStatus) {
                case RUNNING:
                    throw new IllegalStateException("Cannot execute task:"
                            + " the task is already running.");
                case FINISHED:
                    throw new IllegalStateException("Cannot execute task:"
                            + " the task has already been executed "
                            + "(a task can be executed only once)");
            }
        }
    	// 设置运行状态, 调用执行任务前的准备方法, 传入参数, 使用线程池执行任务
        mStatus = Status.RUNNING;
        onPreExecute();
        mWorker.mParams = params;
    	// 这会调用 Runnable 里的 run() 方法
        exec.execute(mFuture);

        return this;
    }
```

一分为二. 在调用 `Executor#execute(Runnable)` 之后, 将根据之前不同的默认的 `Executor` 来执行任务. 一个是串行, 一个是并行. 

串行的内部实现

```java
public static final Executor SERIAL_EXECUTOR = new SerialExecutor();
private static volatile Executor sDefaultExecutor = SERIAL_EXECUTOR;

// AsyncTask#SerialExecutor
private static class SerialExecutor implements Executor {
    	// 非线程安全的数组实现的双端队列
        final ArrayDeque<Runnable> mTasks = new ArrayDeque<Runnable>();
        Runnable mActive;
		// 执行任务时, 把任务添加到队列中, 从队列里依次取出来执行
        public synchronized void execute(final Runnable r) {
            mTasks.offer(new Runnable() {
                public void run() {
                    try {
                        r.run();
                    } finally {
                        scheduleNext();
                    }
                }
            });
            if (mActive == null) {
                scheduleNext();
            }
        }

        protected synchronized void scheduleNext() {
            if ((mActive = mTasks.poll()) != null) {
                // 在这是里使用的是已经创建好的线程池来执行任务, 避免过多创建新线程
                // 减小不必要的消耗. 由于 mTask 取出来的 Runnable 执行方法里, 
                // 我们又递归的调用了 scheduleNext, 所以会按顺序执行下去
                THREAD_POOL_EXECUTOR.execute(mActive);
            }
        }
    }
```

并行的内部实现. 

```java
public static final Executor THREAD_POOL_EXECUTOR;
static {
    // 核心线程 2-4, 最大线程数为 CPU 核心数 + 1, 30s 的超时时间(设置了核心线程也会超时)
    // 有界的等待队列, 最大值为 128, 创建线程的工厂方法重写了以 AsyncTask + number 的线程名
    ThreadPoolExecutor threadPoolExecutor = new ThreadPoolExecutor(
            CORE_POOL_SIZE, MAXIMUM_POOL_SIZE, KEEP_ALIVE_SECONDS, TimeUnit.SECONDS,
            sPoolWorkQueue, sThreadFactory);
    threadPoolExecutor.allowCoreThreadTimeOut(true);
    THREAD_POOL_EXECUTOR = threadPoolExecutor;
}
```

由于 `Executor` 具体执行的是在构造方法里初始化的 `FutureTask#run()`方法, 其中我们传入了一个 `Runnable` 作为参数, 该参数的 run 方法会在这里会被调用. 回过来看构造方法里的

```java
public final AsyncTask<Params, Progress, Result> executeOnExecutor(Executor exec,
            Params... params) {
	/* ... */

    mWorker = new WorkerRunnable<Params, Result>() {
            public Result call() throws Exception {
                // 原子状态, 调用中
                mTaskInvoked.set(true);
                Result result = null;
                try {
                    Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);
                    // 调用定义的方法, 返回结果
                    result = doInBackground(mParams);
                    Binder.flushPendingCommands();
                } catch (Throwable tr) {
                    // 取消
                    mCancelled.set(true);
                    throw tr;
                } finally {
                    // 这会调用之前定义好的 handler 通 message 传送到 onPostExecute 中
                    // result 会被再包一层 AsyncTaskResult 类中, 类中包含 AsyncTask 对象和
                    // result 对象
                    // AsyncTaskResult 可以接收一个结果数组, 但默认 handler 实现只取一个结果
                    postResult(result);
                }
                return result;
            }
        };
		// FutureTask#run 执行时会调用 Callable 里的 call 方法
    	// call 方法的返回值会作为 FutureTask 的调用结果, 通过 Future#get 方法获得
        mFuture = new FutureTask<Result>(mWorker) {
            // 在设置 Future#set 返回值后, 会调用该方法
            @Override
            protected void done() {
                try {
                    // 再次检测运行的结果是否给返回回调
                    postResultIfNotInvoked(get());
                } catch (InterruptedException e) {
                    android.util.Log.w(LOG_TAG, e);
                } catch (ExecutionException e) {
                    throw new RuntimeException("An error occurred while " +
						" executing doInBackground()", e.getCause());
                } catch (CancellationException e) {
                    postResultIfNotInvoked(null);
                }
            }
        };
}
```

关于 AsyncTask 不能执行时间太长(几分钟)的任务, 原因官方并没有解释说明. 在 StackOverflow 上的一个[回答](https://stackoverflow.com/questions/12797550/android-asynctask-for-long-running-operations?noredirect=1&lq=1),  最高票的答案说明了两点原因:

* 没有和 Activity 的生命周期同步
* 易产生内存泄漏

第一点, `doInBackground` 是在非主线程中执行, 之后会在主线程中调用  `onPostExecute` 更新 UI. 但可能原先的 Activity 可能已经被 destroy, 或者重建, AsyncTask 中原 Activity 引用已经不是原来的指向, 这可能引发 Exception. 第二点, 我们很容易在 Activity 中创建一个 AsyncTask 的 inner class, 这使 AsyncTask 中有一个指向 Activity 的引用, 当手机转向等引起的 Activity 重建, 由于 AsyncTask 持有 outer class 的引用, 导致 Activity 不能释放内存



### Reference:

1. <<Android开发艺术探索>>
2. [AsyncTask 源代码](https://android.googlesource.com/platform/frameworks/base/+/oreo-release/core/java/android/os/AsyncTask.java)
3. [https://stackoverflow.com/questions/12797550/android-asynctask-for-long-running-operations?noredirect=1&lq=1](https://stackoverflow.com/questions/12797550/android-asynctask-for-long-running-operations?noredirect=1&lq=1)
4. [https://blog.csdn.net/Gaugamela/article/details/55188752](https://blog.csdn.net/Gaugamela/article/details/55188752)