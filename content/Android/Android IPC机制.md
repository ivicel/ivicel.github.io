title: Android IPC机制
date: 2018-04-01
tag: IPC, Android, 进程间通信





##### 开启多进程的方法

`Android`应用启动时会自动创建一个新的进程, 其进程名默认为**包名**, 为四大组件(`Activity`, `Service`, `ContentProvider`, `Receiver`)启动一个新的进程, 最简单的是在`Manifest.xml`中为其配置`android:process`进程名称. 有两种写法. 

一是指定进程的全称:`android:process="info.ivicel.github.android_ipc.another_process"`, 此时进程为一个全局进程, 其他应用可以通过`ShareUID`方式和它跑在同一进程中

二是简写: `android:process=":remote"`. 这种写法其完整的进程名为`包名:remote`, 并且此时进程为一个私有进程, 其他应用的组件不可以同时跑在该进程中

> 由于`Android`中为不同进程单独分配一个虚拟机来运行, 所以`Android`中不能通过**共享内存**来进行通信. 

由于不能**共享内存**, 便会造成:

1. 静态成员和单例模式完全失效
2. 线程的同步机制完全失效, 通过共享内存来`synchronized`, 锁对象/锁全局类都不是同一个了
3. `SharedPreferences`的可靠性下降. 这是因为`SharedPreferences`底层是通过`xml`文件的来实现的, 需要对文件的读写进行同步
4. `Application`会多次创建. 多进程会为每一个进程启动一`Application`, 相当多次启动应用. 可以在`Application`的`onCreate()`里打印出进程`id`证实启动了多次应用



##### `Android`中`IPC`的几种方式

在`Android`中的`IPC`大致有以下几种: 

* 通过`Intent`的附加`extras`来传递, 其本质是通过`Bundle`来实现的
* 通过共享文件
* 通过`Binder`, 其底层是通过`AIDL`来实现
* 通过`ContentProvider`
* 通过网络`Socket`
* 直接使用`AIDL`
* 通过`Messenger`, 注意这不是消息载体`Message`



1. ###### 使用`Bundle`

   `Bundle`的使用很是简单, 其实现了`Pacelable`接口, 可以直接传递各种可序列化的数据. 

2. ###### 使用共享文件

   可以在进程`A`中写入文件, 在进程`B`中读出文件内容, 要注意的是读出的对象和写入时的对象其内容数据虽然一样, 但本质上是两个对象. 并且使用共享文件进行通信时, 如果要求的并发量过高, 其同步就越困难, 有可能出并发读/写时数据不一致的情况. 其适合使用在对数据同步要求不高的进程之间的通信.
   `SharedPreferences`其底层的实现也是一个`.xml`文件, 但是系统对其读/写时, 会维护一个在内存里的缓存, 这使得多进程模式下对`SharedPreferences`的读写非常不可靠. 所以不要使用其行`IPC`

3. ##### 使用`AIDL`通信

   见 [在Android中使用AIDL进行IPC](./在Android中使用AIDL进行IPC.md)

4. ##### 使用`Messenger`