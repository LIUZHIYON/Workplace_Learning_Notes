# HTTP 请求方法（HTTP 动词）

HTTP 请求方法定义了客户端（浏览器、App）跟服务器说"我想干什么"。

---

## GET 和 POST

### GET — 我要拿数据
浏览器访问任何网址，默认就是 GET。

```
你输入：https://www.google.com/search?q=小夏
浏览器发：GET /search?q=小夏 HTTP/1.1
```

**特点：**
- 数据附在 URL 上（`?key=value`）
- 有长度限制（URL 最多约 2048 个字符）
- 会被浏览器缓存、被收藏、出现在历史记录里
- **不能用来提交密码、修改数据**

**适合：** 搜索、翻页、查看详情、加载图片

### POST — 我要提交数据
填完表单点登录就是 POST。

```
浏览器发：POST /login HTTP/1.1
请求体：username=小夏&password=***
```

**特点：**
- 数据在**请求体**里，URL 上看不到
- 没有长度限制（可以上传大文件）
- 不会被缓存、不会被收藏
- **适合：** 登录、注册、提交订单、上传文件

---

## 全部 HTTP 方法（共 9 种）

用增删改查来理解最直观：

```
数据库操作    HTTP 方法    说明
──────────   ─────────    ──────────────
查（Read）    GET          获取数据
增（Create）  POST         新增数据
改（Update）  PUT          整体替换
改（Update）  PATCH        局部修改
删（Delete）  DELETE       删除数据
```

### 🔍 GET — 查
```http
GET /api/users?page=1 HTTP/1.1
```
获取资源。**幂等**（同样的请求发 100 次，结果一样）。只读。

### ➕ POST — 增
```http
POST /api/users HTTP/1.1
Content-Type: application/json
{"name": "小夏", "age": 18}
```
新增资源。**不幂等**（发两次会新增两条数据）。

### 🔄 PUT — 整体替换
```http
PUT /api/users/1 HTTP/1.1
{"name": "新名字", "age": 20}
```
把 `id=1` 的用户**整个替换**。不传的字段会被清空。**幂等**。

### ✏️ PATCH — 局部修改
```http
PATCH /api/users/1 HTTP/1.1
{"age": 21}
```
只修改 `age` 字段，其他字段不动。**不严格幂等**。

### ❌ DELETE — 删
```http
DELETE /api/users/1 HTTP/1.1
```
删除资源。**幂等**。

---

## 其他方法

| 方法 | 用途 | 常见度 |
|------|------|--------|
| **HEAD** | 跟 GET 一样，但只返回响应头，不返回内容。检查资源是否存在 | ⭐ 偶尔 |
| **OPTIONS** | 问服务器"你支持哪些方法？"。跨域请求（CORS）时会自动发 | ⭐ 偶尔 |
| **CONNECT** | 建立隧道连接，用于 HTTPS 代理 | ❌ 很少用 |
| **TRACE** | 回显请求，调试用（通常禁用） | ❌ 几乎不用 |

---

## 实际开发：RESTful API 风格

日常开发主要就这 5 个方法：

```
GET      /posts              → 获取文章列表
GET      /posts/123          → 获取 id=123 的文章详情
POST     /posts              → 发布新文章
PUT      /posts/123          → 整体更新 id=123 的文章
PATCH    /posts/123          → 修改 id=123 的标题（不改内容）
DELETE   /posts/123          → 删除 id=123 的文章
```

---

## 三个原则

1. **GET 不能修改数据**，这是底线
2. **GET 数据在 URL**，敏感信息不能用 GET
3. **POST/PUT/PATCH/DELETE 是"写"操作**，需要后端做权限校验

> HTML 表单默认只支持 GET 和 POST。用 AJAX（fetch）可以发所有方法。
