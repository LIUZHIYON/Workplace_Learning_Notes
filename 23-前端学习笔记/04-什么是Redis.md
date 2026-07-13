# Redis 是什么？

**Redis** = **Re**mote **Di**ctionary **S**erver（远程字典服务）

> **一个跑在内存里的键值对数据库，快得离谱。**

---

## 核心特点

| 特性 | 说明 |
|------|------|
| **内存存储** | 数据主要在内存里，读写速度微秒级（≈10万+ QPS） |
| **持久化可选** | 可以定期存盘（RDB）或写日志（AOF），重启不丢数据 |
| **数据结构丰富** | 不只是存字符串，还有列表、集合、哈希、有序集合等 |
| **单线程模型** | 避免了锁竞争，原子操作天然支持 |
| **发布/订阅** | 支持消息队列模式 |

---

## 5 种基本数据结构

```bash
# 字符串 — 最常见的
SET user:name "小夏"
GET user:name         # → "小夏"

# 列表 — 双向链表，当队列用
LPUSH queue task1
RPOP queue            # → "task1"

# 哈希 — 存对象，比字符串拼接省事
HSET user:1001 name "小夏" age 18 score 95
HGETALL user:1001

# 集合 — 无序不重复
SADD tags "react" "redis" "docker"
SMEMBERS tags

# 有序集合 — 排行榜神器
ZADD leaderboard 100 "张三" 95 "李四"
ZREVRANGE leaderboard 0 2    # 前三名
```

高级结构：HyperLogLog、Bitmap、GEO、Stream

---

## 典型使用场景

### 🔥 缓存 — 最常用
```text
用户请求 → 查 Redis？有 → 直接返回（快）
               ↓ 没有
            查数据库 → 写入 Redis → 返回
```

### 🔥 Session 存储
用户登录状态存 Redis，多台服务器共享，用户不会掉登录。

### 🔥 排行榜 / 计数器
```bash
INCR article:123:views
```

### 🔥 消息队列
`LPUSH + BRPOP` 或 Redis Stream 实现简单任务队列。

### 🔥 分布式锁
```bash
SET lock:resource_id uuid NX EX 10
```

### 🔥 限流
滑动窗口、令牌桶，用 `INCR + EXPIRE` 实现。

---

## 对比其他技术

| | Redis | MySQL / PostgreSQL | Memcached |
|--|-------|-------------------|-----------|
| 存储位置 | 内存（可持久化） | 磁盘 | 内存（无持久化） |
| 速度 | 微秒级 | 毫秒级 | 微秒级 |
| 数据结构 | 丰富（8+种） | 表/行 | 只有字符串 |
| 存什么 | 热数据、临时数据 | 持久化主数据 | 纯缓存 |
| 容量 | 受内存限制 | 很大 | 受内存限制 |

**常见搭配：** MySQL 存全量数据，Redis 缓存热点数据。

---

## 快速上手

### 安装
```bash
# Docker 最快
docker run --name redis -p 6379:6379 -d redis
```

### 连接
```bash
redis-cli            # 默认连 127.0.0.1:6379
PING                 # 返回 PONG 即成功
```

### 基础命令
```bash
SET name "小夏"
GET name
EXPIRE name 60       # 60秒后自动删除
TTL name             # 查看剩余时间
```

### 在代码里用
```python
import redis
r = redis.Redis(host='localhost', port=6379)
r.set('views', 0)
r.incr('views')  # 1
```

```js
import Redis from 'ioredis'
const redis = new Redis()
await redis.set('views', 0)
await redis.incr('views')
```

> **Redis = 快到你感受不到延迟的内存数据库，适合缓存、排行榜、消息队列等对速度敏感的场景。**
