title: Spring Flasky 开发(三)
date: 2019-05-04
tags: spring boot, flasky

### 1. XSS 保护

> 不要相信用户每一个输入

我们需要对用户写的 post 进行过滤, 以避免 XSS 攻击. 其他的因为 Thymeleaf 默认输出都是 escape 的, 所以我们不需要对像个人 Profile 的信息输入进行过滤. 

```java
// 这里设置一些支持的标签, 比如 span, p, h* 之类
private static final PolicyFactory POLICY_FACTORY = new HtmlPolicyBuilder()
        .allowElements(Const.ALLOWED_HTML_TAG).toFactory();

public static String sanitize(final String text) {
    return POLICY_FACTORY.sanitize(text);
}
```

我们自定义一个 `EntityEventListener`, 在保存 post 到数据库之前对 markdown 和 HTML 过滤.

```java
public class SanitizerListener {
    // 在新插入, 和更新前调用
    @PrePersist
    @PreUpdate
    public void sanitize(Object object) {
        try {
            // 通过反射查找到实体类中被 Sanitize 注解标记的成员变量
            // Sanitize 是自定义的一个注解
            Field[] fields = object.getClass().getDeclaredFields();
            for (Field field : fields) {
                if (field.getAnnotation(Sanitize.class) != null) {
                    // 只支持字符类型
                    log.error(field.getType().toString());
                    if (!CharSequence.class.isAssignableFrom(field.getType())) {
                        log.warn("Annotation @Sanitize only support string field.");
                        continue;
                    }
                    // 通过 bean 反省拿到变量的值, 调用过滤方法后再将值写回
                    PropertyDescriptor descriptor = new PropertyDescriptor(field.getName(), object.getClass());
                    String text = (String) descriptor.getReadMethod().invoke(object);
                    text = CommonUtil.sanitize(text);
                    Method writeMethod = descriptor.getWriteMethod();
                    writeMethod.invoke(object, text);
                }
            }
        } catch (IntrospectionException | IllegalAccessException | InvocationTargetException e) {
            log.error("can't sanitize {}: {}", object, e.getMessage());
        }
    }
}
```

这样我们只需要在实体类 `Post` 和 `Comment` 上加上注解事件, 在成员变量上加入标记注解 `@Sanitize`

```java
@EntityListeners({SanitizerListener.class})
public class Post extends BaseDomain implements Serializable {
    @Sanitize
    private String body;

    @Sanitize
    private String bodyHtml;    
}

@EntityListeners(SanitizerListener.class)
public class Comment extends BaseDomain implements Serializable {
    @Sanitize
    private String body;

    @Sanitize
    private String bodyHtml;
}
```

### 2. 原生 `HttpServletResponse` 对象返回 Thymeleaf 模版

在登录失败时, 我们会提醒返回用户名或密码错误的提示

```java
public class LoginFailureHandler implements AuthenticationFailureHandler {
    @Override
    public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response,
            AuthenticationException exception) throws IOException, ServletException {
        // 获取 Thymeleaf 模版上下文
        WebContext ctx = new WebContext(request, response, request.getServletContext(), request.getLocale());
        // 设置返回 status code
        response.setStatus(HttpStatus.NOT_FOUND.value());
        // 把原用户的输入填回模版中, 避免用户再次输入
        LoginDTO user = new LoginDTO();
        user.setUsername(request.getParameter("username"));
        user.setPassword(request.getParameter("password"));
        user.setRememberMe(request.getParameter("rememberMe") != null);
        ctx.setVariable("user", user);
        ctx.setVariable("msg", "username or password error.");
        ctx.setVariable("classappend", "alert-warning");
        // 当加入 Thymeleaf 依赖时, 自动配置模版处理引擎 bean
        templateEngine.process("auth/login", ctx, response.getWriter());
    }
}
```



项目地址: [https://github.com/ivicel/spring-flasky](https://github.com/ivicel/spring-flasky)

