---

title: "Spring Flasky 开发(二)"
date: 2019-05-03
tags: ["spring boot", "flasky"]
categories: ['Java']

---

### 1. 注册功能

注册需要 4 个字段, 分别是 `username`, `email`, `password`, `confirmPassword`, 注册的 `username` 和 `email` 都是惟一的, 需要从库查找. 两次输入的密码需要相同, 这里自己定义了一个注解约束, 然后实现 ConstraintValidator 接口

```java
// 这个注解作用于类上面, 目标是字段 first 的值要等于字段 second
@Retention(RUNTIME)
@Target(value = {TYPE, ANNOTATION_TYPE})
// 约束的具体实现类
@Constraint(validatedBy = EqualsMatchValidator.class)
public @interface EqualsMatch {
    String first();

    String second();

    String message() default "{first} not equals {second}";

    Class<?>[] groups() default {};

    Class<? extends Payload>[] payload() default {};


    @Documented
    @Target(value = {TYPE, ANNOTATION_TYPE})
    @Retention(RUNTIME)
    @interface List {
        EqualsMatch[] value();
    }
}

public class EqualsMatchValidator implements ConstraintValidator<EqualsMatch, Object> {
    // 字段一名称
    private String firstFieldName;
    // 字段二名称
    private String secondFieldName;

    @Override
    public void initialize(EqualsMatch constraintAnnotation) {
        firstFieldName = constraintAnnotation.first();
        secondFieldName = constraintAnnotation.second();
    }

    // 返回 false 则为不相等, 反之亦然
    @Override
    public boolean isValid(Object value, ConstraintValidatorContext context) {
        // 通过 java bean 反省拿到两个字段的值
        String first = getField(value, firstFieldName);
        String second = getField(value, secondFieldName);
        // 两个都为 null 时
        if (first == null) {
            return second == null;
        }

        return first.equals(second);
    }

    private String getField(Object obj, String name) {
        try {
            PropertyDescriptor descriptor = new PropertyDescriptor(name, obj.getClass());
            Method method = descriptor.getReadMethod();
            return (String) method.invoke(obj);
        } catch (IntrospectionException | IllegalAccessException | InvocationTargetException e) {
            return null;
        }
    }
}
```

### 2. 登录功能

权限控制保护使用的是 Spring Security, 添加 Spring Security 依赖后, 使我们的 `User` 类实现 `UserDetails`, 这是 Spring Security 内置的用户接口, Spring Security 会使用其实现来查找用户的权限认证(Authorization), 以及身份认证(Authentication), 现在我们只需根据数据库中的 `confirmed` 字段来判断用户是否激活了其邮箱, 所以其他的判断都返回 `true`

> 要注意的是 Spring Security 使用的原生的 Servlet Filter 来拦截 request, 有一套自己的拦截顺序, 并不依赖 Spring MVC 框架, 所以如果请求被拦截并不会到达 DispatcherServlet 派发给我们的 Controller

```java
public class User implements UserDetails {
    // 用户的角色集合, 这里我们只有一个, 简单的返回一个 singleton 集合
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singleton(role);
    }

    // 帐号是否非过期
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    // 帐号是否非锁定
    @Override
    public boolean isAccountNonLocked() {
        return true;
    }

    // 认证是否非过期
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    // 帐号是否已启用
    @Override
    public boolean isEnabled() {
        return true;
    }
}
```

接下来是实现一个用户查询, 我们想要的是, 当用户登录时, 会去数据库中查找这个用户, 如果存在返回其信息包装成一个 `UserDetails`, 然后对比其密码. 我们在 `UserServiceImpl` 中实现这个接口

```java
@Service("userService")
public class UserServiceImpl implements UserService, UserDetailsService {
    
    @Override
    public UserDetails loadUserByUsername(String username) 
            throws UsernameNotFoundException {
        Optional<User> user;
        // 根据用户使用的是邮箱还是帐户名登录来查找出
        if (emailPattern.matcher(username).matches()) {
            user = findByEmail(username);
        } else {
            user = findByUsername(username);
        }
        // 帐号不存在
        if (!user.isPresent()) {
            throw new UsernameNotFoundException(String.format("username of %s not found", username));
        }

        return user.get();
    }
}
```

Spring Security 会自动的调用我们上面的实现, 返回 `UserDetails`. 然后对 password 进行对比.

> Spring Security 默认所有的 POST 方法都是有 CSRF 保护

新建一个类继承 `WebSecurityConfigurerAdapter`, 在这里配置登录以及一些拦截, 使用 `@EnableGlobalMethodSecurity(prePostEnabled = true)` 开启 post 请求之前的方法保护, 使用 `@PreAuthorize` 注解, 这使得我们可以保护一些必要的方法, 比如发表 post 必须要先行登录.

```java
// 不要让系统自动配置 
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        // 登录与登出保护, 已登录的不要重复登录, 未登录的不能登出
        // 因为我们使用的是内置 login, logout 拦截, 所以 post 不用自己写 controller
        http.authorizeRequests()
            .antMatchers("/auth/login")
            .access("not @webAuth.loginRequired(authentication)")
            .antMatchers("/auth/logout")
            .access("@webAuth.loginRequired(authentication)");

        // 403 handler
        http.exceptionHandling().accessDeniedHandler(accessDeniedHandler);

        // other urls, 其他 url 都允许
        http.authorizeRequests().anyRequest().permitAll();

        // custom form login, logout
        http.formLogin()
            // 自定义的登录页面, 默认的字段是 username, password
            .loginPage("/auth/login")
            // 登录失败时, 返回用户名或密码错误, 不要返回详细信息, 避免猜解
            .failureHandler(loginFailureHandler)
            // 登录成功后的跳转, 更新最后可见信息等
            .successHandler(loginSuccessHandler)
            .and()
            .logout()
            // 登出控制, 自定义登录 url
            .logoutUrl("/auth/logout")
            // 因为登出是被 filter 拦截的, 并且默认是 POST, 
            // 所以在这给客户端返回一个 JSON, 并给出跳转 url, 由客户端重定向
            .logoutSuccessHandler((request, response, authentication) -> {
                    response.setStatus(HttpStatus.OK.value());
                    response.setContentType(MediaType.APPLICATION_JSON_UTF8_VALUE);
                    Map<String, String> map = new HashMap<>();
                    map.put("url", request.getContextPath() + "/");
                    new ObjectMapper().writeValue(response.getWriter(), map);
                })
            // 清除 sesssion 及 cookie 信息
            .clearAuthentication(true).invalidateHttpSession(true)
            .and().rememberMe();
    }

    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        // 配置我们的登录查询
        // 这里配置后, 登录时系统会查询数据库, 取出匹配数据, 把发送过来的密码
        // 使用 passswordEncoder 加密后, 与库中字段对比
        auth.userDetailsService(userService).passwordEncoder(passwordEncoder);
    }
}
```

在这里, 我们自定义了一个 Bean 用来处理一些常用到的认证, 比如是否登录, 是否是该帐号等, 自定义 [Security Bean](https://docs.spring.io/spring-security/site/docs/current/reference/html5/#el-access-web-beans)

```java
public class WebSecurityAuth {
    // 修改 post 的权限, 本人和管理员都可
    public boolean canModfiyPost(Authentication auth, Post post) {
        // check anonymous
        if (auth == null || !(auth.getPrincipal() instanceof User)) {
            return false;
        }

        return hasPermission(auth, Permission.ADMIN) ||
                (post.getAuthor().equals(auth.getPrincipal()) && hasPermission(auth, Permission.WRITE));
    }
    
    // 修改一些普通个人信息, moderator, 本人, admin
    public boolean canEditProfile(Authentication auth, String username) {
        if (!(auth instanceof User)) {
            return false;
        }

        return auth.getName().equals(username) ||
                AuthorityUtils.authorityListToSet(
            auth.getAuthorities()).contains("ROLE_ADMIN") ||
                AuthorityUtils.authorityListToSet(
            auth.getAuthorities()).contains("ROLE_MODERATOR");
    }

    // 需要登录才可查看
    public boolean loginRequired(Authentication auth) {
        return auth.getPrincipal() instanceof User;
    }

    // 帐户是否激活
    public boolean isConfirmed(Authentication auth) {
        if (auth == null || !(auth.getPrincipal() instanceof User)) {
            return false;
        }

        return ((User) auth.getPrincipal()).isConfirmed();
    }
}
```

> 我们的好多认证都是在 Session 里查找的, 这就要求我们保持同步 Session 里的信息和数据库一样, 比如注册后, 我们是在 A 浏览器里登录, 在 B 里确认了邮箱链接, 那么在确认后, 我们只更改数据库里的字段, 但 A 浏览器使用的是 Session 里的信息, 只能重新登录. 一是要么只使用 `Authentication` 里的 username, 总是去数据库中查找相应数据, 二是要么建立一种 Sync 机制, 要修改数据后将数据同步到 Session Cache 中. Spring Security 没有提供这样同步机制, 因为这机制强烈依赖具体业务, 多久同步, 同步及时或失败是否影响到了业务

### 3. 邮件发送

我们使用的是 `OhMyEmail` 简单邮件发送系统, 基于 SMTP. 因为我们没有使用 spring-boot-mail, 所以 email 的自动配置并不会启动, 首先在设置启动 `@EnableConfigurationProperties({MailProperties.class})`, 用来接收 `spring.mail` 的配置, 然后在 `WebConfig` 里设置 `OhMyEmail` 的配置

```java
@Configuration
public class WebConfig {
    // 依赖内置的 MailProperties
    private MailProperties mailProperties;

    @PostConstruct
    public void initEmail() {
        Properties props = new Properties();
        // 配置用户名, 密码, host, 端口, 和其他的一些配置, 之后使用静态的 builder 即可
        props.setProperty("username", mailProperties.getUsername());
        props.setProperty("password", mailProperties.getPassword());
        props.setProperty("mail.smtp.host", mailProperties.getHost());
        props.setProperty("mail.smtp.port", String.valueOf(mailProperties.getPort()));
        props.putAll(mailProperties.getProperties());

        OhMyEmail.config(props);
    }
}
```

### 4. 自定义的权限检查

如果我们定义一个 Bean, 其实现了 `PermissionEvaluator`, Spring 会自动扫描到这个 Bean 将其用作 `hasPermission` 的检查实现.

```java
public class WebPermissionEvalutor implements PermissionEvaluator {
    // targetDomainObject 一般传进来的是一个 entity, 以检查是否有操作该 entity 的权限
    @Override
    public boolean hasPermission(Authentication authentication, Object targetDomainObject, Object permission) {
        // 这里我们并用不到 targetDomainObject
        // 我们传进来的是一个 Permission 对象
        if (!(permission instanceof Permission) || authentication == null ||
                !(authentication.getPrincipal() instanceof User)) {
            return false;
        }

        User currentUser = (User) authentication.getPrincipal();

        return currentUser.can((Permission) permission);
    }

    @Override
    public boolean hasPermission(Authentication authentication, Serializable targetId, String targetType,
            Object permission) {
        return false;
    }
}
```

### 5. Spring Security Authorize

如果我们需要在普通类中使用 `Authentication` 对象, 可以使用 `org.springframework.security.core.context.SecurityContextHolder` 来获取

```java
Authentication auth = SecurityContextHolder.getContext().getAuthentication();
```

`@PreAuthorize` 和 `@PostAuthorize` 分别是在调用方法前和方法后的认证. 支持 SpEL 表达式, 比如我们可以在用户发表新的 Post 前这样判断当前用户是否有写权限

```java
@PostMapping
@PreAuthorize("hasPermission(null, T(info.ivicel.springflasky.web.model.Permission).WRITE)")
public ResponseEntity addNewPost(Authentication auth, @Validated PostDTO postDto) {
    // ....
}
```

> 参考 [Method Security](https://docs.spring.io/spring-security/site/docs/current/reference/html5/#jc-method)

对于 `hasRole(…)` 这样的角色检查, 我们在实体类 `Role` 实现了 `GrantedAuthority`

```java
public class Role extends BaseDomain implements GrantedAuthority {
    @Override
    public String getAuthority() {
        // 默认检查有前缀 'ROLE_'
        return "ROLE_" + name.toUpperCase();
    }
}
```



项目地址: [https://github.com/ivicel/spring-flasky](https://github.com/ivicel/spring-flasky)