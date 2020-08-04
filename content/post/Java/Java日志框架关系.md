---
title: "Java 日志框架之间的关系"
date: 2019-10-20
tags: ["slf4j", "log4j", "日志"]
categories: ['Java']
---

#### 1. Java 日志框架之间的关系图

![日志框架关系](/images/java日志框架关系.png)

#### 2. 理不清的关系

1. 4 种底层实现: `JUL(java.util.loggging)`, `log4j`, `logback`, `log4j2`即(`log4j-core)`
2. 3 个门面模式: `JCL(commons-loggingg)`, `sfl4j-api`, `log4j-api`(即`log4j2`)
3. 一堆 Adpater: 主要用于同一个门面模式下, 使用不同的底层实现
4. 一堆 Bridge: 主要用于在不修改代码的情况下, 修改底层的实现
