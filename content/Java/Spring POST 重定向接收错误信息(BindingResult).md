title: Spring POST 重定向接收错误信息(BindingResult)
date: 2019-01-10
tags: spring, bindingresult, POST 重定向



#### 1. POST 请求的错误信息重定向

在发送 POST 之后, 如果遇到错误, 我们经常会重定向(GET)回到原页面, 而不是直接返回页面, 这样做是为了避免如果我们点击浏览器刷新按钮时, 会再次发送 POST 请求. 重定向之后, 我们需要获得前面的错误信息.

使用 `@ModelAttribute` 注解来修饰 `RequestMapping` 方法的参数, `ModelAttibute` 注解实际上是接收请求参数, 添加到 Model 中, 在取出后自动删除.

需要注意的几点:

1. 在 GET 处理方法中, 因为我们在渲染的 html/jsp 页面中使用了 `User` 对象, 所以要检测是重定向过来的, 还是用户新的请求来的. 从 POST 重定向过来的, 我们添加了 user 对象, 所以使用 `model.containsAttricute("user")` 来检测. 如果是用户自己的请求, 那么我们生成一个空的 user 对象, 避免渲染页面时出错
2. POST 处理方法中, `BindingResult` 参数一定要跟在 `@Valid` 之后.
3. `RedirectAttributes.addFlashAttribute()` 方法实际是使用了 session, 但会使用后系统自动删除这个属性
4. `BindingResult` 类内的错误信息的 key 值是 `BindingResult.class.getName() + "." + ModelAttribute修饰的名称`. 如 `org.springframework.validation.BindingResult.user`

```java
@RequestMapping(value = "/register", method = RequestMethod.GET)
public String register(Model model) {
    // 注意检测 user 对象, 不能在参数中添加 User 参数, 这会优先使用从页面请求参数
    if (!model.containsAttribute("user")) {
        model.addAttribute(new User());
	}
    return "register";
}

// BindingResult 只能跟在 @Valid 后面才会起作用
@RequestMapping(value = "/register", method = RequestMethod.POST)
public String register(@Valid @ModelAttribute("user") User user,
                       BindingResult bindingResult,
                       RedirectAttributes ra) {
    if (bindingResult.hasErrors()) {
      ra.addFlashAttribute("user", user);
      // user 对象对应的 BindingResult 错误信息, 注意其 key 名
      ra.addFlashAttribute("org.springframework.validation.BindingResult.user",
                         bindingResult);
      return "redirect:/register";
    }
    return "redirect:/login";
}
```

#### 2. Thymeleaf 中错误信息的使用

在 thymeleaf 中使用 `#fields` 来获得 form 的错误消息. 比如有一个 form, 其提交的是一个 User 对象. 

```html
<!-- register.html -->
<form th:object="${user}" th:action="@{/register}">
  <input th:name="*{username}" th:value="*{username}">
  <!-- 在这里获到错误消息, 检查 username 字段是否有错误消息, 
		th:errors 会自动提取对应的 field 中的错误信息 -->
  <span th:errors="*{username}" th:if="${#fields.hasErrors('username')}"></span>
</form>
```

#### Reference:

1. https://stackoverflow.com/questions/2543797/spring-redirect-after-post-even-with-validation-errors/10049138#10049138