title: Spring 数据库事务处理
date: 2019-01-12
tags: spring 事务, spring 开发, 事务传播



#### 1. 事务的传播行为

事务的传播行为是 Spring 对数据库事务添加的特定功能, 指的是当方法 A 调用另一个方法 B 时, B 事务中所采取的不同策略的行为, 比如新建事务, 挂起事务等. 事务的传播注解修饰的是方法 B 自己, 当被别的方法调用时才起的作用, 而不是方法内起作用

#### 1.1 Spring 中七种事务传播行为

| 事务传播行为类型               | 说明                                                         |
| ------------------------------ | ------------------------------------------------------------ |
| **`PROPAGATION_REQUIRED`**     | 1. 如果当前没有事务, 则新建一个事务<br />2. 有的话就则加入到这个事务中 |
| PROPAGATION_SUPPORTS           | 有则沿用, 没有也不新建<br />1. 如果当前存在事务, 则沿用当前事务 <br />2. 如果当前没有事务, 就以非事务方式运行 |
| PROPAGATION_MANDATORY          | 确保必须使用当前事务<br />1. 如果当前存在, 使用当前事务. <br />2. 如果当前没有事务, 就抛出异常 |
| **`PROPAGATION_REQUIRES_NEW`** | 总是新建自己事务, 这样新事务总是拥有新的锁和隔离级别等特性, 如果当前存在事务, 先把当前事务挂起. |
| PROPAGATION_NOT_SUPPORTED      | 确保以非事务运行<br />1. 当前不存在事务, 以非事务方式运行<br />2. 如果当前存在事务则先挂起当前事务, 以非事务运行 |
| PROPAGATION_NEVER              | 确保当前没有事务<br />1. 以非事务方式运行<br />2. 如果当前存在事务则抛出异常 |
| **`PROPAGATION_NESTED`**       | 1. 如果当前存在事务, 是嵌套在事务内运行<br />2. 如果当前没有事务, 创建新的事务来运行, 但与 `PROPAGATION_REQUIRED` 不同的是, 内部方法发生的异常不会当前方法的 SQL |

> 加**黑体**的三个是常用的

#### 2. 传播行为的代码测试

在数据库中有两张表 `t_user1` 和 `t_user2`, 以及对应 POJO, 简单的 Service 操作

> 下方所有的 `test*()` 方法都应该在不在 `User1Service` 或 `User2Service` 类内, 避免产生类内自调用

```java
// 表 t_user1 对应的 POJO
public Class User1 {
		private Long id;
  	private String name;
  	// getters and setters...
}

// 表 t_user2 对应的 POJO
public Class User2 {
		private Long id;
  	private String name;
  	// getters and setters...
}
```

##### 2.1 `PROPAGATION_REQUIRED` 行为

```java
// user1 和 user2 的 service 的插入操作都在事务中, 传播都为 PROPAGATION_REQUIRED
public class User1Service {
		@Transactional(propagation = Propagation.REQUIRED)
  	public void addRequired(User1 user1) {
      	// Mybatais mapper: insert into `t_user1` (`name`) values (#name)
      	user1Mapper.insert(user1);
    }
}

public class User2Service {
		@Transactional(propagation = Propagation.REQUIRED)
  	public void addRequired(User2 user2) {
      	user2Mapper.insert(user2);
    }
  
  	@Transactional(propagation = Propagation.REQUIRED)
  	public void addRequiredWithException(User2 user2) {
      	user2Mapper.insert(user2);
      	throw new RuntimeException("手动抛出异常");
    }
}
```

* 在外围非事务的方法中调用, 各个事务都是相对独立的, 成功或失败都不互相干扰

```java
// 测试一
public void test1(){
    User1 user1 = new User1();
    user1.setName("张三");
    user1Service.addRequired(user1);

    User2 user2=new User2();
    user2.setName("李四");
    user2Service.addRequired(user2);
		// 即使在最后抛出异常, 上面的两个独立事务都插入成功
    throw new RuntimeException();
}

// 测试二
public void test2(){
    User1 user1 = new User1();
    user1.setName("张三");
    user1Service.addRequired(user1);

    User2 user2 = new User2();
    user2.setName("李四");
	  // 在 user2Service 抛出异常, 
  	// 但 user1Service, user2Service 是两个独立事务,
  	// 所以 user1Service 插入成功, user2Service 失败
    user2Service.addRequiredWithException(user2);
}
```

* 在外围调用方法是开启事务时, 这时的要将被调用方法加入到这个事务当中而不是自己新创建事务

```java
// 三个测试都开启了事务

// 测试一
@Transactional
public void test1(){
    User1 user1 = new User1();
    user1.setName("张三");
    user1Service.addRequired(user1);

    User2 user2=new User2();
    user2.setName("李四");
    user2Service.addRequired(user2);
		// user1Service, user2Service 都加入了当前方法的同一事务当中
  	// 所以最后事务抛出异常时, 所有的插入都失败
    throw new RuntimeException();
}

// 测试二
@Transactional
public void test2(){
    User1 user1 = new User1();
    user1.setName("张三");
    user1Service.addRequired(user1);

    User2 user2 = new User2();
    user2.setName("李四");
	  // user1Service, user2Service 都加入了当前方法的同一事务当中
  	// 当内部方法抛出异常时, 事务回滚, 则所有的插入都失败
    user2Service.addRequiredWithException(user2);
}

// 测试三
@Transactional
public void test2(){
    User1 user1 = new User1();
    user1.setName("张三");
  	// 依赖外围方法事务, 成功插入
    user1Service.addRequired(user1);

    User2 user2 = new User2();
    user2.setName("李四");
	  
  	try {
      	// user1Service, user2Service 都加入了当前方法的同一事务当中
  			// 当内部方法抛出异常时, 在外围方法捕获, 处理了这些异常, 事务还是成功的
      	// user2 插入失败
	    	user2Service.addRequiredWithException(user2);
    } catch (Exception e) {
      	
    }
}
```

##### 2.2 `PROPAGATION_REQUIRED_NEW` 行为

```java
// user1 和 user2 的 service 的插入操作都在事务中
public class User1Service {
		@Transactional(propagation = Propagation.REQUIRES_NEW)
  	public void addRequiresNew(User1 user1) {
      	// Mybatais mapper: insert into `t_user1` (`name`) values (#name)
      	user1Mapper.insert(user1);
    }
  
  	@Transactional(propagation = Propagation.REQUIRED)
  	public void addRequired(User1 user1) {
      	// Mybatais mapper: insert into `t_user1` (`name`) values (#name)
      	user1Mapper.insert(user1);
    }
}

public class User2Service {
		@Transactional(propagation = Propagation.REQUIRES_NEW)
  	public void addRequiresNew(User2 user2) {
      	user2Mapper.insert(user2);
    }
  
  	@Transactional(propagation = Propagation.REQUIRES_NEW)
  	public void addRequiresNewWithException(User2 user2) {
      	user2Mapper.insert(user2);
      	throw new RuntimeException("手动抛出异常");
    }
}
```

* 外围调用方法没有添加事务

```java
// 测试一
public void test1() {
    User1 user1 = new User1();
    user1.setName("张三");
    user1Service.addRequiresNew(user1);

    User2 user2 = new User2();
    user2.setName("李四");
    user2Service.addRequiresNew(user2);
  	// 调用方法抛出异常, 但两个内部方法都是自己很生成自己的事务, 互不影响, 都成功插入新数据
  	throw new RuntimeException();
}

// 测试二
public void test2() {
    User1 user1 = new User1();
    user1.setName("张三");
  	// 内部方法一独立的事务, 成功插入新数据
    user1Service.addRequiresNew(user1);

    User2 user2 = new User2();
    user2.setName("李四");
  	// 内部方法二自己抛出异常, 自回滚自己的事务
    user2Service.addRequiresNewWithException(user2);
}
```

* 外围调用方法是在事务中

```java
// 测试一, 测试外围事务的异常对内部方法的影响
@Transactional
public void test1() {
    User1 user1 = new User1();
    user1.setName("张三");
  	// Propagation.REQUIRED 会加入到外部事务中, 外部事务回滚则插入失败
    user1Service.addRequired(user1);

    User2 user2 = new User2();
    user2.setName("李四");
  	// Propagation.REQUIRED_NEW 会自己创建新的事务来运行, 无论外部事务如何, 插入数据成功
    user2Service.addRequiresNew(user2);
		// 外围事务回滚
    throw new RuntimeException();
}
// 测试二, 测试内部方法在自己新创建的事务对其他内部方法的影响
@Transactional
public void test2() {
    User1 user1 = new User1();
    user1.setName("张三");
  	// 依赖外围事务, 插入失败
    user1Service.addRequired(user1);

    User2 user2 = new User2();
    user2.setName("李四");
  	// 自己新创建事务, 插入成功
    user2Service.addRequiresNew(user2);

    User2 user3 = new User2();
    user3.setName("王五");
  	// 自己新创建事务, 抛出异常, 并且异常向调用方法抛出, 自已的事务回滚, 外围事务也回滚
    user2Service.addRequiresNewWithException(user3);
}
// 测试三, 与测试二惟一不同的是, 新创建的事务向外围抛出的异常在外围事务中捕获并处理了
@Transactional
public void test3() {
    User1 user1 = new User1();
    user1.setName("张三");
  	// 插入成功, 依赖外围事务
    user1Service.addRequired(user1);

    User2 user2 = new User2();
    user2.setName("李四");
  	// 插入成功, 自己新创建的事务
    user2Service.addRequiresNew(user2);

    User2 user3 = new User2();
    user3.setName("王五");
    try {
      	// 插入失败, 自己创建的事务, 然后把异常抛到了外围方法, 在这里处理了异常
        user2Service.addRequiresNewWithException(user3);
    } catch (Exception e) {
    }
}
```

##### 2.3 `PROPAGATION_NESTED` 行为

该行为在外围开启事务时, 内部方法嵌套在外围事务中运行, 外围事务的回溯导致内部方法也一起回滚; 而内部方法的事务则可以自己单独回滚, 不用影响到外围的事务

>`PROPAGATION_NESTED` 事务嵌套行为需要数据库中的**保存点(save point)**, Hibernate 并不支持这个功能, 会抛出: `JpaDialect does not support savepoints - check your JPA provider's capabilities` 异常

```java
public class User1Service {
 		@Transactional(propagation = Propagation.NESTED)
    public void addNested(User1 user1) {
        user1Mapper.insert(user1);
    } 
}

public class User2Service {
    @Transactional(propagation = Propagation.NESTED)
    public void addNested(User2 user2) {
        user2Mapper.insert(user2);
    }

    @Transactional(propagation = Propagation.NESTED)
    public void addNestedWithException(User2 user2) {
        user2Mapper.insert(user2);
        throw new RuntimeException("抛出异常");
    }  
}
```

* 外围方法没有开启事务

```java
// 测试一, 外围方法抛出异常
public void test1() {
    User1 user1 = new User1();
    user1.setName("张三");
    // 创建新事务, 插入成功
    user1Service.addNested(user1);

    User2 user2 = new User2();
    user2.setName("李四");
    // 创建新事务, 插入成功
    user2Service.addNested(user2);
    // 外围抛出的异常
    throw new RuntimeException();
}

// 测试二, 内部方法抛出异常
public void test2() {
    User1 user1 = new User1();
    user1.setName("张三");
    // 创建新事务, 插入成功
    user1Service.addNested(user1);

    User2 user2 = new User2();
    user2.setName("李四");
    // 创建新事务, 自己回滚事务, 插入失败
    user2Service.addNestedWithException(user2);
}
```

* 外围方法开启事务

```java
// 测试一, 外围方法抛出异常
@Transactional
public void test1() {
    User1 user1 = new User1();
    user1.setName("张三");
  	// 创建新事务, 嵌套在外围事务中, 插入失败
    user1Service.addNested(user1);

    User2 user2 = new User2();
    user2.setName("李四");
	  // 创建新事务, 嵌套在外围事务中, 插入失败
    user2Service.addNested(user2);
  	// 外围事务的回滚影响内部方法的事务
    throw new RuntimeException();
}

// 测试二, 内部方法抛出异常
@Transactional
public void test2() {
    User1 user1 = new User1();
    user1.setName("张三");
  	// 创建新事务, 嵌套在外围事务中, 插入失败
    user1Service.addNested(user1);

    User2 user2 = new User2();
    user2.setName("李四");
	  // 内部方法的异常抛到了外围事务中, 所有的插入都失败
    user2Service.addNestedWithException(user2);
}

// 测试三, 内部方法抛出异常并有外围捕获
@Transactional
public void test2() {
    User1 user1 = new User1();
    user1.setName("张三");
  	// 创建新事务, 嵌套在外围事务中, 插入成功
    user1Service.addNested(user1);

    User2 user2 = new User2();
    user2.setName("李四");
	  // 内部方法的异常抛到了外围事务中并被处理, 内部方法插入失败
  	try {
	    user2Service.addNestedWithException(user2);
    } catch(Exception e) {}
}
```

#### 2. `@Transactional` 自调用类中方法失效问题

Spring 的事务处理是基于 AOP, 通过动态代理生成一个类的代理对象, 而当我们在类的方法中再调用同一个类的事务方法, 其实际还是在同一个事务中, 是类自身的调用, 而不是代理调用, 这样就还是在同一次 AOP 中.

```java
@Service("userService")
public class UserServiceImple implements IUserService {
 		@Override
  	@Transactional
  	public void insertUsers(List<User> users) {
     		for (User user : users) {
          	// 调用自已类自身的方法, 还是处于同一 AOP 处理中
         		insertUser(user); 
        }
    }
  
  	@Transactional(propagation = Propagation.REQUIRES_NEW)
  	public void insertUser(User user) {
     		userMapper.insert(user); 
    }
}
```

也可以通过手动每次获取类的代理对象, 来手动调用类的方法

```java
@Service("userService")
public class UserServiceImple implements IUserService, ApplicationContextAware {
  	private ApplicationContext applicationContext;
  
 		@Override
  	@Transactional
  	public void insertUsers(List<User> users) {
      	// 从 IoC 容器中取出代理对象
      	IUserService userService = applicationContext.getBean(IUserService.class);
     		for (User user : users) {
          	// 使用代理对象来调用类方法, 这样总是能通过 AOP
         		userService.insertUser(user); 
        }
    }
  
  	@Transactional(propagation = Propagation.REQUIRES_NEW)
  	public void insertUser(User user) {
     		userMapper.insert(user); 
    }
  	
  	// spring 框架在扫描包时, 会对生成的 bean 检查其是否实现了 ApplicationContextAware 接口
  	// 如果实际了则会调用 setApplicationContext 方法, 并把当前 Spring 上下文容器作为参数
  	@Override
  	public void setApplicationContext(ApplicationContext applicationContext) 
      			throws BeansException {
        this.applicationContext = applicationContext;
    }
}
```























