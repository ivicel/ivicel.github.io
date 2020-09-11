---

title: "Spring Security 和 JWT 认证及授权(一).md"
date: 2020-08-03
tags: ["spring", "spring security"]
categories: ['Java']
typora-root-url: ../../../static
draft: true
---

## 1. Spring Security 的工作方法及概念

Spring Security 主要是通过一系列的 Servelet Filter 来调用. 在 Spring web 中, 所有的请求都会先发送到 `DelegatingFilterProxy` 这个是代理的 Filter, 然后会派发到 Spring Security 的 `FilterChainProxy` 

![SecurityFilterChain](/images/securityfilterchain.png)

* **SecurityContext**: 上下文, 用于保存当前认证的对象, 只是一个 `Authentication` 的 wrapper

* **SecurityContextHolder**: 上下文的工具类, 用来创建, 获取和清除 `SecurityContext` 上下文. 默认的创建策略是使用 ThreadLocal 来保证 SecurityContext 惟一性

* **Authentication**: 认证接口对象, 比如使用用户名密码来认证的 `UsernamePasswordAuthenticationToken`

* **AuthenticationManager**: 认证接口, 只有一个认证方法, 默认的实现是 `ProvideManager`, 里面有一个 `AuthenticationProvider` 的列表, 在认证时是会按顺序调用 `AuthenticationProvider#supports` 方法检查该实现是否支持某个方式认证

  ```java
  public interface AuthenticationManager {
  	/*
  	 * 认证方法, 传入未认证过的 authentication 返回已认证的 authentication
  	 * 如果认证失败会抛出异常然后被 HttpSecurity#exceptionHandling 里配置的处理
  	 */
  	Authentication authenticate(Authentication authentication)
  			throws AuthenticationException;
  }
  ```

  







































