title: MyBatis Generator XML 配置详解
date: 2019-01-01
tags: mybatis



#### 1. 配置文件

固定的文件头, 约束和根结点

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE generatorConfiguration
	PUBLIC "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN"
	"http://mybatis.org/dtd/mybatis-generator-config_1_0.dtd">
<generatorConfiguration>
    <!-- .... -->
</generatorConfiguration>
```

##### 1.1 `properties` 标签

用于引入外部的 `properties` 文件, 只能出现一次或者不使用, 并且如果使用的话要保证其在配置文件的最开始位置

*  `resource` 属性, 使用 `classpath` 来指定资源路径.  `resource=test/mypackage/my.properties` 指的是包 `test.mypackage` 下的 `my.properties` 文件
* `url` 属性, 使用文件路径, 比如 `url=file:///c:/myfolder/my.properties`

##### 1.2 `classPathEntry` 标签

使用时位置要放在 `properties` 标签后面, 并且有 `context` 标签之前, 用来引入其他 java 的 ZIP/JAR 包, classpath, 或者目录, 可以出现多次

* `location` 属性, 比如用来引用 mysql 包,  `location=F:/mysql/mysql-connector.jar`

##### 1.3 `context` 标签

用于指定一组生成对象的环境配置, 至少一个或者多个

###### 1.3.1  `context` 标签的属性

* `id` 必选, 用来确定标签惟一性
* `defaultModeType`: 用于指定 MBG 如何生成实体类. 
  1. `conditional` 默认值, 如果一个表只含有一个字段, 比如只单有一个主键, 那么不会为该表单独生成一个实体类, 而是合并到基类中
  2. `flat` 为每张表生成一个单独的实体类, 推荐使用
  3. `hierarchical` 如果表有主键则为该表生成一个单独的实体类, 如果表还有 BLOB 字段, 则为表生成一个包含所有 BLOB 字段的单独实体类, 然后为所有其他的字段另外生成一个单独的实体类. MBG 为类之间维护一个继承关系
* `targetRuntime` 用于指定生成代码的运行环境, 可选 
  1. `MyBatis3`: 默认值. 
  2. `MyBatis3Simple` 选这个时不会生成相应的 Example 方法. 
  3.  `MyBatis3DynamicSql` 生成兼容 MyBatis 3.4.2 和 Java 8 及以上版本的对象, 依赖于 MyBatis 动态 SQL
* `introspectedColumnImpl` 该属性可以指定扩展 `org.mybatis.generator.api.IntrospectedColumn` 类的实现类

###### 1.3.2 `context` 标签子标签

* `property` 0 个或多个. 

  * `autoDelimitKeywords` 根据包 `org.mybatis.generator.internal.db.SqlReservedWords` 类中自动给关键字添加分隔符
  * `beginningDelimiter` 分隔符开始
  * `endingDelimiter` 分隔符结束
  * `javaFileEncoding` 设置 Java 文件的编码
  * `javaFormatter` Java 类名格式方法. 默认为类`org.mybatis.generator.api.dom.DefaultJavaFormatter`, 自定义类则要实现 `org.mybatis.generator.api.JavaFormatter`
  * `xmlFormatter` XML 文件的名字生成格式

* `plugin` 0 个或多个, 用来定义扩展插件. 多个插件将按配置顺序来先后执行. 

  `org.mybatis.generator.plugins.CachePlugin` 是一个缓存插件, 可以生成 SQL XML 映射文件中的 cache 标签, 只有当 targetRuntime 为 MyBatis3 时插件才有效

* `commentGenerator` 0 个或多个, 用来配置如何生成注释信息.

  * `type` 属性, 用来指定一个实现了 `org.mybatis.generator.api.CommentGenerator` 接口的类, 该类用来生成注释信息. 默认值为 `DEFAULT`, 默认类为 `org.mybatis.generator.internal.DefaultCommentGenerator`

  三个可选的属性标签, 需要通过 `property` 标签来指定

  * `suppressAllComments` 阻止生成注释, 默认为 `false`
  * `suppressDate` 阻止生成注释包含时间戳, 默认 `false`
  * `addRemarkComments` 注释是否添加数据库表的备注信息, 默认 `false`

* `jdbcConnection` 1 个. 配置连接数据库方式.

  * `driverClass` 必选属性. JDBC 驱动程序的完全限定类名
  * `connectionURL` 必选属性, JDBC 的连接 URL
  * `userId` 可选属性, 访问数据库的用户名
  * `password` 可选属性, 访问数据库的密码

  除 4 个属性外, 还可以添加 property 子标签, 用于连接数据库其他所需要的属性

* `javaTypeResolver` 0 个或 1 个, 用于数据库类型与 Java 类型的映射关系.

  * `type` 可选属性. 用于如何映射类型关系, 自定义的话需要类实现 `org.mybatis.generator.api.JavaTypeResolver`, 另外还接受一个默认 `DEFAULT` 值
  * `forceBigDecimals` 子标签 `property` 属性, 默认为 `false`, 用于设置数据库 `DECIMAL` 和 `NUMERIC` 类型强制映射为 Java 的 `java.math.BigDecimal` 类型, 默认情况下的转换规则为.
    1. 精度 > 0 或 长度 > 18, 就转换成 `java.math.BigDecimal`
    2. 精度 = 0 并且 10 <= 长度 <= 18, 转成 `java.lang.Long`
    3. 精度 = 0 并且 5 <= 长度 <= 9, 转成 `java.lang.Integer`
    4. 精度 = 0 并且 长度 < 5, 转成 `java.lang.Short`
  * `useJSR310Types` 设置使用 JSR-310 来为时间和日期(`DATE`, `TIME`, `TIMESTAMP`)转换, 而不是使用 `java.util.Date` 类. 不管如何设置, 这两个类型转换都是固定的. 1.  JDBC Type `TIME_WITH_TIMEZONE` ---> `java.time.OffsetTime`, 2. `TIMESTAMP_WITH_TIMEZONE` ---> `java.time.OffsetDateTime`. 当设置为 `true` 时:
    1. JDBC Type: `DATE` ---> `java.time.LocalDate`
    2. `TIME` ---> `java.time.LocalTime`
    3. `TIMESTAMP` ---> `java.time.LocalDateTime`

* `javaModelGenerator` 1 个. 用来配置如何生成 java 实体类. 两个必选属性:

  * `targetPackage` 生成实体类存放的包名
  * `targetProject` 目标项目的路径, 比如 Maven 中  `src/main/java`

  其他支持的 property 子标签属性

  * `constructorBased` 只对 MyBatis3 有效, 使用构造方法入参, 如果为 `false` 则使用 setter 方法. 默认 `false`
  * `enableSubPackages` 如果为 `true`, 则会根据 catalog 和 schema 来生成子包, 否则使用 targetPackage 属性, 默认 `false`
  * `immutable` 默认 `false`, 设置生成实体类对象后, 对象不可变, 即不会生成 setter 方法
  * `rootClass` 所有实体类的基类, 值是类的完全限定名. 子类不会覆盖和父类中完全匹配的属性. 1. 属性名完全相同. 2. 属性类型相同. 3. 属性有 getter 方法 4. 属性有 setter 方法
  * `trimStrings` 设置是否要对数据库查询结果进行 trim 操作, 默认 false

* `sqlMapGenerator` 0 个或 1 个, 用于配置生成 Mapper.xml 文件的属性. 当 targetRuntime 设置为 MyBatis3 时, 如果在 `javaClientGenerator` 中配置指明需要 XML 的配置, 此标签才必须要配置, 不然该标签是可选的

  * `targetPackage` 生成实体类存放的包名
  * `targetProject` 目标项目的路径, 比如 Maven 中  `src/main/java`

  如果没有配置 `javaClientGenerator` 标签, 那么按以下规则:

  * 如果指定了一个 `sqlMapGenerator`, 那么按这个配置生成
  * 如果没有指定 `sqlMapGenerator`, 那么只生成实体类

  另外还一个 `enableSubPackages` 的子 property 标签

* `javaClientGenerator` 0 个或者 1 个. 如果不配置该标签, 则不会生成 Java Mapper 接口. 有 3 个必选属性

  1. `type` 用于选择 Mapper 接口生成器, 自定义实现需要继承 `org.mybatis.generator.codegen.AbstractJavaClientGenerator` 类, 根据 targetRuntime 的值可以分成两类.
     * targetRutime 为 `MyBatis3` 时
       * ANNOTATEDMAPPER` 基于注解的 Mapper 接口, 不会有对应的 XML 映射文件
       * `MIXEDMAPPER` XML 和注解的混合形式, 上面这种情况中的 SQL Provider 廨方法会被 XML 方式替代
       * `XMLMAPPER` 所有的方法都在 XML 中, 接口调用依赖 XML 文件
     * targetRuntime 为 `MyBatis3Simple` 时
       * `ANNOTATEDMAPPER` 基于注解的 Mapper 接口
       * `XMLMAPPER` 所有的方法都在 XML 中, 接口调用依赖 XML 文件

* `table` 1 个或者多个, 用于配置需要通过内省数据库的表, 只有配置过的表, 才会生成对应的 Java 代码.

  * `tableName` 必选属性, 如果设置为 `%`, 则匹配所有表

  1. ###### 其他可选的属性

    * `schema` 数据库的 schema, 可以使用 SQL 通配符匹配. 如果设置了该值, 生成的 SQL 的表名会变成如 schema.tableName 形式
    * `catalog` 数据库的 catalog, 如果设置了该值, 生成的 SQL 表名会变成 catalog.tableName 形式
    * `alias` 如果指定, 这个值会用在生成的 select 查询 SQL 表的别名和列名上, 例如 alias_actualColumnName
    * `domainObjectName` 生成对象的基本名称, 如果没有指定则根据表名来生成名称
    * `enableXXX` XXX 代表多种 SQL 方法, 用来指定是否生成对应的 XXX 语句
    * `selectByPrimaryKeyQueryId` 和 `selectByExampleQueryId`: 用于 DBA 跟踪工具
    * `modelType` 和 context 中的 defaultModelType 含义相同, 覆盖该值 
    * `escapeWildcards` 查询列是否对 schema 和表名中 SQL 通配符(`_` 和 `%`)进行转义
    * `delimitIdentifiers` 是否给标识符增加分隔符, 默认为 false
    * `delimitAllColumns` 是否对所有列添加分隔符, 默认为 false

  2. ###### 其他的 property 子标签属性

    * `constructorBased` 构造方法, 和 javaModelGenerator 一样
    * `ignoreQualifiersAtRuntime` 生成的 SQL 中的表名将不会包含 schema 和 catalog 前缀
    * `immutable` 和 javaModelGenerator 中含义相同
    * `modeOnly` 用于配置是否只生成实体类, 如果为 `true`, 就不会有 Mapper 接口, 并覆盖属性中的 enableXXX 方法
    * `rootClass`, `rootInterface` 和 javaModelGenerator 中的属性一样
    * `runtimeCatalog` 运行时的 catalog, 当生成表和运行环境表的 catalog 不一样时可以使用该属性进行配置
    * `runtimeSchema` 运行时的 schema, 当生成表和运行环境表的 schema 不一样时可以使用该属性进行配置
    * `selectAllOrderByClause` 该属性值会追加到 `selectAll` 方法后的 SQL 中, 直接与 order by 拼接后添加到 SQL 末尾
    * `useActualColumnNames` 如果为 true, 那么 MBG 会使用从数据库元数据获取的列名作为生成的实体对象的属性, 否则使用驼峰式名称, 可以通过 columnOverride 标签显式指定, 此时将忽略该属性
    * `userColumnIndexes` 如果为 true, MBG 生成 resultMaps 时会使用索引而不是结果中列名的顺序
    * `useCompoundPropertyNames` 如果为 true, MBG 生成属性名时会将列名和列备注连接起来

  3. `generatedKey` 0 个或 1 个, 用来指自动生成主键的属性(identity 字段或者 sequences 序列), 当指定这个标签时, MBG 将在生成 insert 的 SQL 映射文件中插入一个 selectKey 标签, 该标签有以下属性

    * `column` 必选, 生成列的列名
    * `sqlStatement` 必选, 返回新值的 SQL 语句, 如果这是一个 identity 语句, 则可以使用一个预定义的特殊值.(`Cloudscape`, `DB2`, `DB2_MF`, `Derby`, `HSQLDB`, `Informix`, `MySQL`, `SQL Server`, `SYBASE`, `JDBC`)
    * `type` 当 type 为 post 并且 identity 为 true 时, 生成的 selectKey 中 order = AFTER; 当 type 为 pre, identity 只能为 false, 生成的 selectKey 中 order = BEFORE. 自动增长的列只有插入到数据库后才能得到 ID, 所以只能是 AFTER, 当使用序列时, 只有先获取序列之后才能插入数据库, 所以是 BEFORE
    * `identity` 当设置为 true 时, 该列会被标记为 identity 列, 并且 selectKey 标签会被插入在 insert 后面. 否则 selecteKey 会被插入 insert 之前, 默认 false

  4. `columnRenamingRule` 0 个或 1 个, 可以使用该标签在生成列之前对列进行重命名. 该标签有一个必选属性 `searchString`, 可选属性 `replaceString`. MBG 内部使用 `java.util.regex.Matcher.replaceAll` 来实现替换功能

  5. `columnOverride` 0 个或多个. 该标签用于将某些默认计算的属性值更改为指定的值. 除 column 属性是必选属性

     * `column` 必选 , 表示要重写的列名
     * `property` 要使用的 Java 属性的名称, 如果没有指定, MBG 会根据列名生成
     * `javaType` 列的属性值为完全限定的 Java 类型, 如果需要, 可以覆盖 JavaTypeResolver 计算出的类型
     * `jdbcType` 列的 JDBC 类型, 如 INTEGER, DECIMAL, NUMERIC, VARCHAR..
     * `typeHandler` 根据用户定义的需要用来处理列的类型处理器. 必须是一个继承自 TypeHandler 接口的全限定的类名. 如果没有指定或者是空白, MyBatis 会用默认的类型处理器.
     * `delimitedColumnName` 指定是否应在生成的 SQL 的列名称上增加分隔符. 如果列的名称中包含空格, MBG 会自动添加分隔符

  6. `ignoreColumn` 0 个或多个, 用来屏蔽不需要生成的列, column 属性指定表列名, delimitedColumnName 用于表示是否要区别大小写进行列名匹配

      



















