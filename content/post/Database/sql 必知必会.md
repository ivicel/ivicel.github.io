---
title: 'SQL 简单速记'
date: 2017-03-20
tags: ['sql']
categories: ['Database']
---

### **1. 检索数据**

```sql
/* 单个列 */
SELECT prod_name FROM Product;
/* 多个列 */
SELECT prod_id, prod_name FROM Products;
/* 所有列 */
SELECT * FROM Products;
/* 检索不同值 */
SELECT DISTINCT vend_id FROM Products;
/* 条件限制 */
SELECT prod_id FROM Products WHERE prod_id = 5;
SELECT prod_id FROM Products LIMIT 5;
/* 注释 */
/*...多行注释*/
--- 单行注释
```

### **2. 排序**

```sql
/* 排序条件不一定出现在选择结果中 */

/* 排序单个列 */
SELECT * FROM  Products ORDER BY prod_id;
/* 多个列排序 */
SELECT prod_id, prod_name FROM Products ORDER BY prod_id, prod_name;
/* 按位置排序，即选择结果中的位置，prod_id,prod_name */
SELECT prod_id, prod_name FROM Products ORDER BY 1, 2;
/* 降序，默认升序 ASC */
SELECT prod_id FROM Products ORDER BY prod_name DESC;
```

### **3. 过滤数据**

```sql
/* WHREE子句 */
SELECT * FROM Products WHERE prod_id < 5;

```

| 操作符  | 说明         |
| ------- | ------------ |
| =       | 等于         |
| <>      | 不等于       |
| !=      | 不等于       |
| <       | 小于         |
| <=      | 小于等于     |
| !       | 不小于       |
| \>      | 大于         |
| \>=     | 大于等于     |
| !>      | 不大于       |
| BETWEEN | 在指定值之间 |
| IS NULL | 为 NULL      |

### **4. 高级过滤**

```sql
/* AND、OR */
SELECT prod_id, prod_name FROM Products WHERE prod_id = 5 AND prod_name = 'hello';
SELECT prod_id, prod_name FROM Products WHERE prod_id = 5 OR prod_name = 'hello';

SELECT prod_name, prod_price
FROM Products
WHERE vend_id = 'DLL01' OR vend_id = 'BRS01'
AND prod_price >= 10;

/* IN */
SELECT prod_name, prod_id
FROM Products
WHERE vend_id IN ('DLL01', 'BRS01')
ORDER BY prod_name;

/* NOT */
SELECT prod_name, prod_id
FROM Products
WHERE NOT prod_id = 5;
```

### **5. 通配符过滤**

```sql
/* % 任意字符出现任意次, 匹配多个字符*/
SELECT prod_name, prod_id
FROM Products
WHERE prod_name LIKE 'fish%';

/* _ 匹配单个字符 */
SELECT prod_name, prod_id
FROM Products
WHERE prod_name LIKE 'fish_';

/* [] 匹配方括号内指定字符 */
SELECT prod_name, prod_id
FROM Products
WHERE prod_name LIKE '[JM]%';


```

### **6. 创建字段**

```sql
SELECT vend_name + ' (' + vend_country + ')'
FROM Vendors
ORDER BY vend_name;
/* 或者, 具体依赖于具体的数据库 */
SELECT vend_name || ' (' || vend_country || ')'
FROM Vendors
ORDER BY vend_name;

/* AS 别名 */
SELECT vend_name + ' (' + vend_country + ')' AS vend_title
FROM Vendors
ORDER BY vend_name;

/* 算术计算 "+, -, *, \" */
SELECT prod_id, quantity, item_price, quantity * item_price AS expanded_price
FROM OrderItems
WHERE order_num = 2008;
```

### **7. 数据处理函数**

各个数据库函数的名称可能不同

| 函　　数             | 语　　法                                                                                                                                                     |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 提取字符串的组成部分 | Access 使用 MID()；DB2、Oracle、PostgreSQL 和 SQLite 使用 SUBSTR()；MySQL 和 SQL Server 使用 SUBSTRING()                                                     |
| 数据类型转换         | Access 和 Oracle 使用多个函数，每种类型的转换有一个函数；DB2 和 PostgreSQL 使用 CAST()；MariaDB、MySQL 和 SQL Server 使用 CONVERT()”                         |
| “取当前日期          | Access 使用 NOW()；DB2 和 PostgreSQL 使用 CURRENT_DATE；MariaDB 和 MySQL 使用 CURDATE()；Oracle 使用 SYSDATE；SQL Server 使用 GETDATE()；SQLite 使用 DATE()” |
| 取当前日期           | Access 使用 NOW()；DB2 和 PostgreSQL 使用 CURRENT_DATE；MariaDB 和 MySQL 使用 CURDATE()；Oracle 使用 SYSDATE；SQL Server 使用 GETDATE()；SQLite 使用 DATE()” |

- 文本处理函数

| 函　　数                                | 说　　明                                    |
| --------------------------------------- | ------------------------------------------- |
| LEFT()（或使用子字符串函数）            | 返回字符串左边的字符                        |
| LENGTH()（也使用 DATALENGTH()或 LEN()） | 返回字符串的长度                            |
| LOWER()（Access 使用 LCASE()）          | 将字符串转换为小写                          |
| LTRIM()                                 | 去掉字符串左边的空格                        |
| RIGHT()                                 | （或使用子字符串函数） 返回字符串右边的字符 |
| RTRIM()                                 | 去掉字符串右边的空格                        |
| SOUNDEX()                               | 返回字符串的 SOUNDEX 值                     |
| UPPER()（Access 使用 UCASE()）          | 将字符串转换为大写”                         |

- 聚集函数

| 函　　数 | 说　　明         |
| -------- | ---------------- |
| AVG()    | 返回某列的平均值 |
| COUNT()  | 返回某列的行数   |
| MAX()    | 返回某列的最大值 |
| MIN()    | 返回某列的最小值 |
| SUM()    | 返回某列值之和”  |

```sql
SELECT AVG(DISTINCT prod_price) AS avg_price
FROM Products
WHERE vend_id 'DLL01';
```

### **8. 分组**

```sql
/* GROUP BY 组合条件必须出现在选择结果中*/
SELECT vend_id, COUNT(*) AS num_prods
FROM Products
GROUP BY vend_id;

/* HAVING 与 GROUP BY 一同使用来过滤分组*/
SELECT vend_id, COUNT(*) AS num_prods
FROM Products
GROUP BY vend_id
HAVING COUNT(*) >= 2;

/* 分组后排序 */
SELECT order_num, COUNT(*) AS items
FROM OrderItems
GROUP BY order_num
HAVING COUNT(*) >= 3
ORDER BY items, order_num;
```

### **9. 子查询**

```sql
SELECT cust_name, cust_contact
FROM Customers
WHERE cust_id IN (
    SELECT cust_id FROM Order WHERE order_num IN (
        SELECT order_num FROM OrderItems WHERE prod_id = 'RGA001'
    )
);

SELECT cust_name, cust_state, (
    SELECT COUNT(*) FROM Orders WHERE cust_id = cust_id) AS orders
FROM Customers
ORDER BY cust_name;
```

### **10. 联结**

```sql
/* 使用联结时一定要有限定条件 WHERE， LIKE等 */

/* 多表查询 */
SELECT vend_name, prod_name, prod_price
FROM Vendors, Products
WHERE Vendors.vend_id = Products.vend_id;

/* 内联结 */
SELECT vend_name, prod_name, prod_price
FROM Vendors INNER JOIN Products
ON Vendors.vend_id = Products.vend_id;

/* 左外联结 */
SELECT Customers.cust_id, Orders.order_num
FROM Customers LEFT OUTER JOIN Orders
ON Customers.cust_id = Orders.cust_id;

/* 右外联结 */
SELECT Customers.cust_id, Orders.order_num
FROM Customers RIGHT OUTER JOIN Orders
ON Orders.cust_id = Customers.cust_id;


/* 表自联结 */
SELECT cust_id, cust_name, cust_contact
FROM Customers
WHERE cust_name = (
    SELECT cust_name FROM Customers WHERE cust_contact = 'Jim Jones'
);

SELECT c1.cust_id, c1.cust_name, c1.cust_contact
FROM Customers AS c1, Customers AS c2
WHERE c1.cust_name = c2.cust_name
AND c2.cust_contact = 'Jim Jones';
```

### **11. 组合查询**

```sql
SELECT cust_name, cust_contact, cust_email
FROM Customers
WHERE cust_state IN ('IL','IN','MI');

SELECT cust_name, cust_contact, cust_email
FROM Customers
WHERE cust_name = 'Fun4All';


/* 以上两条使用 UNION 来查询*/
SELECT cust_name, cust_contact, cust_email
FROM Customers
WHERE cust_state IN ('IL','IN','MI')
UNION
SELECT cust_name, cust_contact, cust_email
FROM Customers
WHERE cust_name = 'Fun4All';”

/* UNION默认去掉重复的行，使用ALL包含所有行*/
SELECT cust_name, cust_contact, cust_email
FROM Customers
WHERE cust_state IN ('IL','IN','MI')
UNION ALL
SELECT cust_name, cust_contact, cust_email
FROM Customers
WHERE cust_name = 'Fun4All';
```

### **12. 数据插入**

```sql
/* 必须与库中顺序对齐 */
INSERT INTO Customers
VALUES('1000000006',
       'Toy Land',
       '123 Any Street',
       'New York',
       'NY',
       '11111',
       'USA',
       NULL,
       NULL);

/* 插入部分数据 */
INSERT INTO Customers(
    cust_name,
    cust_address,
    cust_city,
    cust_state,
    cust_zip,
    cust_country
)
VALUES(
    'Toy Land',
    '123 Any Street',
    'New York',
    'NY',
    '11111',
    'USA'
);

/* 使用检出行插入数据 */
INSERT INTO Customers(cust_id,
                      cust_contact,
                      cust_email,
                      cust_name,
                      cust_address,
                      cust_city,
                      cust_state,
                      cust_zip,
                      cust_country)
SELECT cust_id,
       cust_contact,
       cust_email,
       cust_name,
       cust_address,
       cust_city,
       cust_state,
       cust_zip,
       cust_country
FROM CustNew;

/* 从一个表复制到另一个表 */
SELECT * INTO CustCopy FROM Customers;
```

### **13. 更新数据**

```sql
/* 更新数据时不要忘记限制条件，否则会更新整个表的所有行 */
UPDATE Customers SET cust_email = 'kil@there.com' WHERE cust_id = '100005';

/* 删除行 */
DELETE FROM Customers WHERE cust_id = '100005';
```

### **14. 创建表**

```sql
CREATE TABLE Products
(
    prod_id     CHAR(10)        NOT NULL,
    vend_id     CHAR(10)        NOT NULL,
    prod_name   CHAR(254)       NOT NULL,
    prod_price  DECIMA(8, 2)    NOT NULL,
    prod_desc   VARCHAR(1000)   NULL
);


CREATE TABLE OrderItems
(
    order_num      INTEGER          NOT NULL,
    order_item     INTEGER          NOT NULL,
    prod_id        CHAR(10)         NOT NULL,
    quantity       INTEGER          NOT NULL      DEFAULT 1,
    item_price     DECIMAL(8,2)     NOT NULL
);

/* 更新表结构 */
ALTER TABLE Vendors
ADD vend_phone CHAR(128);

ALTER TABLE Vendors
DROP COLUMN vend_phone;

/* 删除表 */
DROP TABLE CustCopy;
```

### **15. 视图**

```sql
/* 虚拟的表 */
CREATE VIEW ProductCustomers AS
SELECT cust_name, cust_contact, prod_id
FROM Customers, Orders, OrderItems
WHERE Customers.cust_id = Orders.cust_id
AND OrderItems.order_num = Orders.order_num;
```
