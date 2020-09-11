---

title: "Spring Security 的使用"
date: 2019-01-03
tags: ["spring", "spring security"]
categories: ['Java']
lastmod: 2020-08-08

---



## 1. Spring Security 的开启方式

在 Java Web 中一般使用 Filter 来对请求进行拦截, Spring Security 基于此来对在进入 DispatcherServlet 前对 Spring MVC 进行请求拦截, 进行统一难, 从而决定是否放行

* 如果使用 `web.xml` 进行配置, Spring Security 提供了一个 `DelegatingFilterProxy` 的 Filter 代理器, 只要在 `web.xml` 中配置该 Filter
* 如果使用注解方式, 则在配置中加入 `@EnableWebSecurity`, 该注解会自动生成一个 `SecurityFilterChain` 的 Spring Bean, 该 Bean 包含一个 Filter List, 所有的请求都会由 DelegatingFilterProxy 派发到 Filter List 中
* 如果使用的是 Spring Boot, 在添加 spring-boot-starter-security 依赖后, 根据 srping boot 的自动配置机制, 会对所有的路由进行 security 拦截, 其实际启用了 `@EnableWebSecurity`. 如果手动启用该配置, 那么会覆盖自动配置设置

启用 spring security 之后, 默认会对所有的路由路径进行认证, 默认的用户名为 user, 默认的密码会在每次启动程序时随机生成, 打印在 INFO 日志中. Spring Boot 在 `application.properties` 中有 `spring.security.*` 配置可以设置简单的配置项

一般我们都会使用继承 `WebSecurityConfigurerAdapter` 来自定义更加复杂精确的过滤, 主要实现其中 3 个方法

* `configure(AuthenticationManagerBuilder auth)` 用来配置用户签名, 主要是 user-details 机制, 给予用户赋予用户名, 密码, 角色, 加载用户权限
* `configure(HttpSecurity http)` 用来配置拦截保护请求, 决定哪些请求放行, 哪些请求需要验证
* `configure(WebSecurity web)` 用来配置 Filter 链

## 2. 验证用户(用户名, 密码, 角色...)

### 2.1 使用内存签名

在 Spring 5 之后要求使用一个密码编码器, 用来对密码进行加密以及密码匹配, 其要实现接口 `PasswordEncoder`, 以使用内存签名服务为例

```java
@Override
protected void configure(AuthenticationManagerBuilder auth) throws Exception {
    // 设置使用内在签名验证
 	auth.inMemeoryAuthentication()
        // 设置使用的密码编码器
        .passwordEncoder(new BCryptPasswordEncoder())
        // 添加用户
        .withUser("admin")
        // 设置用户密码
        .password("123456")
        // 设置用户角色, 可以添加多个角色, roles() 
        // 方法内部实质调用了 .authorities() 方法, 其会在角色名前自动添加前缀 `ROLE_`
        // 如果我们使用 .authorities() 方法, 则需要手动添加前缀
        .roles("USER", "ADMIN")
        // 使用 and() 来连接多个角色
        .and()
        .withUser("user")
        .psssword("123456")
        .roles("USER");
}
```

`withUser()` 方法返回的是一个用户详情构造器 `UserDetailsBuilder`, 其还有以下的常用的方法

* `accountExpired(boolean)` 账号是否过期
* `accountLocked(boolean)` 是否锁定账号
* `credentialsExpired(boolean)` 定义凭证是否过期
* `disabled(boolean)` 是否禁用用户
* `username(String)` 定义用户名

### 2.2 使用数据库定义用户认证服务

`AuthenticationManagerBuilder#jdbcAuthentication` 方法会返回  `JdbcUserDetailsManagerConfigurer` 对象, 数据库用户表为  `org.springframework.security.core.userdetails.User`, 数据库至少要实现 4 个字段(`id`, `username`, `password`, `available`), 并且这顺序是固定的, 另外角色的权限表, 权限表要实现 2 个字段(`id`, `name`), 并且顺序也是固定的, 角色权限查询返回的是一个 List.

如果没有实现自己的查询方法, 则会使用内部的查询类 `org.springframework.security.core.userdetails.jdbc.JdbcDaoImpl`

```java
@Override
protected void configure(AuthenticationManagerBuilder auth) throws Exception {
    // 使用 JDBC 认证
 	auth.jdbcAuthentication()
        .passwordEncoder(new BCryptPasswordEncoder())
        .dataSource(dataSource)
        // 设置使用 username 查询的 SQL
        .usersByUsernameQuery("SELECT user_name, pwd, available FROM t_user " +
                              " WHERE user_name = ?")
        // 设置查询角色的 SQL
        .authoritiesByUsernameQuery("SELECT u.user_name, r.role_name FROM " + 
                               		" t_user u, t_user_role ur, t_role r WHERE " +
                                    " u.id = ur.user_id AND r.id = ur.role_id AND " +
        							" u.user_name = ?");
}
```

如果需要实现自己的查询处理, 那么可以使用 `AuthenticationManagerBuilder#userDetailsService()` 方法, 其参数是实现了 `UserDetailsService` 接口的类, 只有一个方法 `loadUserByUsername`, 该方法返回 `UserDetails` 对象, 需要自己实现该接口

```java
// 用户模型
public class User implements UserDetails {
	private String username;
	private String password;
	private boolean isEnabled;
    private boolean isAccountNonExpired;
    private boolean isAccountNonLocked;
    private boolean isCredentialsNonExpired;
    private List<? extends GrantedAuthority> authorities;

    public User(String username, String password, boolean enabled,
               isAccountNonExpired, isAccountNonLocked, isCredentialsNonExpired,
               authorities) {
        // 这些值从数值库中查出后传入
        this.username = username;
        this.password = password;
        this.enabled = enabled;
        this.isAccountNonExpired = isAccountNonExpired;
        this.isAccountNonLocked = isAccountNonLocked;
        this.isCredentialsNonExpired = isCredentialsNonExpired;
        this.authorities = authorities;
    }
    // getter and setter ...
}


// WebMvcSecurity 配置
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    private JdbcTemplate jdbcTemplate;
	@Override
	protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth.userDetailsService((username) -> jdbcTemplate.queryForObject(userQuery,
				(rs, rowNum) -> {
            if (rs.isAfterLast()) {
                return null;
            }
            // 假设数据库用户为 id, username, password, enabled
            String password = rs.getString(2);
            boolean enabled = rs.getInt(3) == 1;
            return new User(username, password, enabled);
        }, username))
        	// 设置密码编码方式
        	.passwordEncoder(new BCryptPasswordEncoder());
    }
}
```

## 3. 限制请求(对 url 的配置)

限制请求主要是对不同的路径(url)实现不同的策略, 通过这能够实现对不同角色赋予不同权限.

```java
@Override
protected void configure(HttpSecurity http) throws Exception {
    // 开启认证
 	http.authorizeRequests()   
        // Ant 风格匹配, 限定 /user/welcome, /user/details 的访问必须为 ADMIN 或 USER 
        .anMatchers("/user/welcome", "/user/details").hasAnyRole("ADMIN", "USER")
        // /admin 下的 url, 注意 hasAuthority 的角色名称, 自动添加 ROLE_ 前缀
        .antMatchers("/admin/**").hasAuthority("ROLE_ADMIN")
        // 其他任何路径都允许访问
        .anyReuqest().permitAll()
        .and().anonymous()
        // Spring Security 默认的登录页面
        .and().formLogin()
        // 开启 HTTP 基础验证
        .and().httpBasic();
}
```

* `access(String)` 参数为 SpEL, 返回 true 则允许访问
* `anonymous()` 允许匿名访问
* `authorizeRequest()` 限定通过签名请求
* `anyRequest()` 限定任意的请求
* `hasAnyRole(String...)` 将访问权限赋予多个角色(自动添加前缀 ROLE_)
* `hasRole(String)` 将访问权限赋予一个角色
* `permitAll()` 无条件允许访问
* `and()` 连接词
* `httpBasic()` 启动浏览器 HTTP 基础验证
* `formLogin()` 启用默认的登录页面
* `not()` 对其他方法的访问采取求反
* `fullyAuthenticated()` 如果是完整验证(并非 Remember-me), 则允许访问
* `denyAll()` 不允许访问
* `hasIpAddress(String)` 指定 IP 可以访问
* `rememberme()` 开启 remember-me 功能
* `hasAuthority(String)` 指定角色可以访问, 需要自己添加前缀 ROLE_
* `hasAnyAuthority(String...)` 指定的多角定可以访问, 需要自己添加前缀 ROLE_
* `regexMatchers(String)` 正则表达式匹配

有时候我们需要更加强大的验证功能, 可以使用 SpEL(Spring 表达式), 比如 `access("hasRole('USER') or hasRole('ADMIN')")` 来表示需要 USER 或 ADMIN 角色

## 4. 自定义登录页面

在登录页面都有一个 Remember Me 的功能, 默认的实现是**记住一天**, 记录在浏览器的 Cookie 中, 其键为 `remember-me-key`, 其值为 MD5 Hash 过的值

```java
@Override
protected void configure(HttpSecurity http) throws Exception {
 	http.authorizeRequests().antMatchers("/admin/**").access("hasRole('ADMIN')")
        // 启用 remember me 功能, 设置其时间限制和 cookie key
        .and().rememberMe().tokenValiditySeconds(7 * 24 * 3600).key("remember-me")
        .and().authorizeRequests().antMatchers("/**").permitAll()
        // 设置自定义的登录路由
        .and().formLogin().loginPage("/login/page")
        // 设置登录成功后的跳转路径
        .defaultSuccessUrl("/admin/welcome")
        // 设置自定义登出路由
        .and().logout().logoutUrl("/logout/page")
        // 登出后跳转页面
        .logoutSuccessUrl("/welcome");
}
```

## 5. 防止跨站请求伪造(CSRF)

添加 Spring Security 后, 会自动添加 CSRF 认证, 可以使用 `HttpSecurity#csrf().disable()` 来关闭. Spring Security 会生成一个 `_csrf` 变量, 可以在页面模版中使用这个变量

```html
<input type=hidden id="${_csrf.parameterName}" name="${_csrf.parameterName}" 
	value="${_csrf.token}">
```















































