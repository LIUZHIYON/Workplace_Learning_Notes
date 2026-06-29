# 🌐 HTTP 协议详解

## 1. 什么是 HTTP？

**HTTP（HyperText Transfer Protocol，超文本传输协议）** 是互联网上应用最广泛的协议之一。它定义了客户端（浏览器、App）与服务器之间如何通信，采用 **请求-响应模型**。

```text
客户端                         服务器
   │                             │
   │────── HTTP Request ────────→│
   │                             │
   │←──── HTTP Response ────────│
   │                             │
```

### 核心特点

| 特点 | 说明 |
|------|------|
| **无状态** | 每个请求之间相互独立，服务器不记忆之前的请求 |
| **明文传输** | HTTP 本身不加密（HTTPS 解决此问题） |
| **客户端驱动** | 总是客户端发起请求，服务器被动响应 |
| **灵活可扩展** | 通过 Header 可以扩展功能 |

---

## 2. HTTP 请求与响应结构

### 请求结构

```http
POST /api/users HTTP/1.1
Host: example.com
Content-Type: application/json
Authorization: Bearer xxx

{"name": "Alice", "age": 25}
```

```
┌─────────────────────────────────┐
│ 请求行 (Request Line)            │
│ POST /api/users HTTP/1.1       │
├─────────────────────────────────┤
│ 请求头 (Headers)                 │
│ Host: example.com              │
│ Content-Type: application/json │
│ Authorization: Bearer xxx      │
├─────────────────────────────────┤
│ 空行 (CRLF)                     │
├─────────────────────────────────┤
│ 请求体 (Body) — 可选             │
│ {"name": "Alice", "age": 25}  │
└─────────────────────────────────┘
```

### 响应结构

```http
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: session_id=abc123

{"id": 1, "name": "Alice", "age": 25}
```

```
┌──────────────────────────────────┐
│ 状态行 (Status Line)              │
│ HTTP/1.1 200 OK                 │
├──────────────────────────────────┤
│ 响应头 (Response Headers)         │
│ Content-Type: application/json  │
│ Set-Cookie: session_id=abc123   │
├──────────────────────────────────┤
│ 空行 (CRLF)                      │
├──────────────────────────────────┤
│ 响应体 (Body) — 可选              │
│ {"id": 1, "name": "Alice"}     │
└──────────────────────────────────┘
```

---

## 3. HTTP 请求方法 (Methods)

```mermaid
mindmap
  HTTP请求方法
    GET
      获取资源
      幂等
      参数在URL中
    POST
      创建资源
      非幂等
      参数在Body中
    PUT
      全量替换资源
      幂等
    PATCH
      部分更新资源
      幂等
    DELETE
      删除资源
      幂等
    HEAD
      类似GET，但只返回Header
    OPTIONS
      查询服务器支持的Method
    CONNECT
      建立隧道代理(HTTPS)
    TRACE
      回显请求(调试用)
```

### 常用方法对比

| 方法 | 幂等 | 安全 | 是否有 Body | 用途 |
|------|------|------|-------------|------|
| GET | ✅ | ✅ | ❌ | 查询资源 |
| POST | ❌ | ❌ | ✅ | 创建资源 |
| PUT | ✅ | ❌ | ✅ | 全量更新 |
| PATCH | ❌ | ❌ | ✅ | 部分更新 |
| DELETE | ✅ | ❌ | ❌ | 删除资源 |

> **幂等**：同一个请求执行多次，结果相同
> **安全**：不会改变服务器状态

---

## 4. HTTP 状态码 (Status Codes)

```mermaid
flowchart TD
    Start["服务器返回状态码"] --> Category{"第一位数字"}

    Category -->|"1xx<br/>信息性"| 1xx["100 Continue<br/>101 Switching Protocols<br/>102 Processing"]
    Category -->|"2xx<br/>成功"| 2xx["200 OK<br/>201 Created<br/>204 No Content"]
    Category -->|"3xx<br/>重定向"| 3xx["301 Moved Permanently<br/>302 Found<br/>304 Not Modified"]
    Category -->|"4xx<br/>客户端错误"| 4xx["400 Bad Request<br/>401 Unauthorized<br/>403 Forbidden<br/>404 Not Found<br/>429 Too Many Requests"]
    Category -->|"5xx<br/>服务端错误"| 5xx["500 Internal Server Error<br/>502 Bad Gateway<br/>503 Service Unavailable<br/>504 Gateway Timeout"]

    style Start fill:#6366f1,color:#fff
    style Category fill:#8b5cf6,color:#fff
    style 1xx fill:#60a5fa,color:#fff
    style 2xx fill:#34d399,color:#fff
    style 3xx fill:#fbbf24,color:#1f2937
    style 4xx fill:#fb923c,color:#fff
    style 5xx fill:#f87171,color:#fff
```

### 常见状态码速查表

| 状态码 | 含义 | 说明 |
|--------|------|------|
| **200** | OK | 请求成功 |
| **201** | Created | 资源创建成功（POST 常见） |
| **204** | No Content | 成功但无返回体（DELETE 常见） |
| **301** | Moved Permanently | 永久重定向 |
| **302** | Found | 临时重定向 |
| **304** | Not Modified | 缓存有效（配合 `If-Modified-Since`） |
| **400** | Bad Request | 请求格式错误 |
| **401** | Unauthorized | 未认证（需登录） |
| **403** | Forbidden | 无权限 |
| **404** | Not Found | 资源不存在 |
| **405** | Method Not Allowed | 不允许的方法 |
| **429** | Too Many Requests | 请求频率超限 |
| **500** | Internal Server Error | 服务器内部错误 |
| **502** | Bad Gateway | 网关/代理错误 |
| **503** | Service Unavailable | 服务暂时不可用 |
| **504** | Gateway Timeout | 网关超时 |

---

## 5. HTTP 版本演进

```mermaid
timeline
    title HTTP 协议版本演进
    1991 : HTTP/0.9
         : 只有 GET，无 Header，无状态码
    1996 : HTTP/1.0
         : 增加 Header、状态码、多种 Method
         : 每个请求新建 TCP 连接
    1997 : HTTP/1.1
         : 持久连接 (Keep-Alive)
         : 管道化 (Pipelining)
         : 分块传输 (Chunked Transfer)
    2015 : HTTP/2
         : 多路复用 (Multiplexing)
         : 二进制分帧
         : 头部压缩 (HPACK)
         : 服务器推送 (Server Push)
    2022 : HTTP/3
         : 基于 QUIC (UDP)
         : 0-RTT 连接建立
         : 更好的弱网表现
```

### 版本对比表

| 特性 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|------|----------|--------|--------|
| 传输层 | TCP | TCP | **QUIC (UDP)** |
| 连接复用 | ❌ 串行 | ✅ 多路复用 | ✅ 多路复用 |
| 头部压缩 | ❌ | ✅ HPACK | ✅ QPACK |
| 队头阻塞 | ✅ 有 | ⚠️ TCP 层级 | ❌ 消除 |
| 服务器推送 | ❌ | ✅ | ✅ |
| 连接建立 | 3 次握手 | 3 次握手 | 0-RTT |
| 加密 | 可选 (HTTPS) | 事实上强制 | 强制 |

### 队头阻塞 (Head-of-Line Blocking)

```
HTTP/1.1  请求串行发送 ─── 一个慢了后面全等
┌─────┐    ┌─────┐    ┌─────┐
│ Req1 │───→│ Req2 │───→│ Req3 │
└─────┘    └─────┘    └─────┘
     ←────── 必须等 Req1 返回 ──────→

HTTP/2   请求并发复用同一条 TCP 连接
┌─────┐────┐
│ Req1 │   │   Stream 1
├─────┤   ├───┼───
│ Req2 │   │   Stream 3
├─────┤   │   │
│ Req3 │   │   Stream 5
└─────┘   ┘   │
             TCP Connection
```

---

## 6. HTTPS — 安全的 HTTP

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant CA as 证书颁发机构(CA)

    Note over Client,Server: TLS 握手阶段
    Client->>Server: 1. ClientHello (支持的加密套件、TLS版本)
    Server->>Client: 2. ServerHello + 证书 (含公钥)
    Client->>CA: 3. 验证证书签名
    CA-->>Client: 证书有效
    Client->>Client: 4. 生成 Pre-Master Secret
    Client->>Server: 5. 用公钥加密发送 Pre-Master Secret
    Server->>Server: 6. 用私钥解密得到会话密钥
    Server->>Client: 7. 握手完成 (Finished)

    Note over Client,Server: HTTPS 加密通信阶段
    Client->>Server: ──[加密]── HTTP 请求 ────────→
    Server->>Client: ←──[加密]── HTTP 响应 ──────│
```

### HTTP vs HTTPS

| 对比项 | HTTP | HTTPS |
|--------|------|-------|
| 端口 | 80 | 443 |
| 加密 | ❌ 明文 | ✅ TLS/SSL 加密 |
| 数据完整性 | ❌ 可篡改 | ✅ 防篡改 |
| 身份验证 | ❌ 无 | ✅ 证书验证 |
| 性能 | 快 | 稍慢（多一次握手） |
| SEO | ❌ 排名低 | ✅ 排名高 |

---

## 7. HTTP 缓存机制

```mermaid
flowchart LR
    Client["浏览器/客户端"] -->|"1. 请求资源"| Cache["缓存层"]
    Cache -->|"2. 缓存有效？"| Check{"Cache-Control<br/>max-age 判断"}

    Check -->|"✅ 新鲜 (Fresh)"| Hit["返回缓存 (200 from cache)"]
    Check -->|"❌ 过期 (Stale)"| Server["向服务器验证"]

    Server -->|"304 Not Modified"| Renew["续期缓存"]
    Server -->|"200 + 新资源"| Update["更新缓存"]

    Renew --> Hit
    Update --> Hit

    style Hit fill:#34d399,color:#fff
    style Check fill:#fbbf24,color:#1f2937
    style Renew fill:#60a5fa,color:#fff
    style Update fill:#60a5fa,color:#fff
```

### 缓存相关 Header

| Header | 方向 | 说明 |
|--------|------|------|
| `Cache-Control: max-age=3600` | 响应 | 缓存有效期（秒） |
| `Cache-Control: no-cache` | 响应 | 每次需验证 |
| `Cache-Control: no-store` | 响应 | 禁止缓存 |
| `ETag: "hash123"` | 响应 | 资源唯一标识 |
| `If-None-Match: "hash123"` | 请求 | 配合 ETag 做条件请求 |
| `Last-Modified: Wed, 21 Oct 2023` | 响应 | 最后修改时间 |
| `If-Modified-Since: ...` | 请求 | 配合 Last-Modified |

---

## 8. RESTful API 设计规范

```mermaid
flowchart TD
    subgraph 资源路径设计
        GET["GET /api/users"] --> List["获取用户列表"]
        GET1["GET /api/users/:id"] --> Detail["获取单个用户"]
        POST["POST /api/users"] --> Create["创建用户"]
        PUT["PUT /api/users/:id"] --> Update["全量更新用户"]
        PATCH["PATCH /api/users/:id"] --> Partial["部分更新用户"]
        DELETE["DELETE /api/users/:id"] --> Delete["删除用户"]
    end

    subgraph 命名约定
        N1["✅ /api/users"] --> P1["复数名词"]
        N2["✅ /api/users/:id/orders"] --> P2["资源层级"]
        N3["❌ /api/getUsers"] --> P3["不要用动词"]
        N4["❌ /api/userList"] --> P4["不要用驼峰"]
    end

    style GET fill:#34d399,color:#fff
    style POST fill:#60a5fa,color:#fff
    style PUT fill:#fbbf24,color:#1f2937
    style PATCH fill:#fb923c,color:#fff
    style DELETE fill:#f87171,color:#fff
```

---

## 总结

```mermaid
mindmap
  HTTP核心要点
    请求-响应模型
      客户端发起请求
      服务器返回响应
      无状态协议
    状态码
      2xx 成功
      3xx 重定向
      4xx 客户端错误
      5xx 服务端错误
    版本
      HTTP/1.1 持久连接
      HTTP/2.0 多路复用
      HTTP/3.0 QUIC+UDP
    安全
      HTTPS = HTTP + TLS
      证书验证身份
      加密传输数据
    缓存
      Cache-Control
      ETag / If-None-Match
      减少重复请求
```

---

> **一句话总结：HTTP 是 Web 的基石，理解它的请求/响应结构、状态码、缓存和版本演进，是后端开发的基本功。**
