# Flask 是什么？

Flask 是一个 Python 写的**轻量级 Web 框架**，核心思想：**小而灵活**。

> 给你最基本的东西，剩下的你自己选 —— 不像 Django 那样什么都帮你安排好。

---

## 最小示例

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, 小夏!'

if __name__ == '__main__':
    app.run()
```

访问 `http://127.0.0.1:5000/` 就看到 "Hello, 小夏!"。

---

## 核心功能

| 功能 | 说明 |
|------|------|
| **路由** | `@app.route('/user/<name>')` — URL 参数、GET/POST |
| **模板** | 自带 Jinja2 模板引擎，服务端渲染 HTML |
| **请求/响应** | `request.args`、`request.form`、`jsonify()` |
| **会话** | 简单的 Cookie-based session |
| **蓝图** | 把路由分组，项目大了也不会乱 |

---

## 经典使用场景

### 1. 给硬件/嵌入式设备搭 API
几十行代码给开发板搭一个 Web 控制界面（视频流、录制控制、文件下载）。

### 2. 写 REST API
```python
@app.route('/api/users', methods=['GET'])
def get_users():
    users = db.query('SELECT * FROM users')
    return jsonify(users)
```

### 3. 快速原型 / MVP
新想法用 Flask 搭个 demo 验证，半小时就够了。

### 4. 微服务
大项目拆成小服务，每个服务几十行 Flask 代码 + 一个数据库。

### 5. 内部工具 / 运维后台
日志查看、配置管理、数据导入导出。

### 6. 文件服务器 / 下载站
用 `send_file` 提供文件下载。

---

## 常用扩展

```text
Flask-SQLAlchemy     → 数据库 ORM
Flask-Migrate        → 数据库迁移
Flask-Login          → 用户登录认证
Flask-RESTful        → 快速写 REST API
Flask-SocketIO       → WebSocket（实时通信）
Flask-CORS           → 跨域
```

需要什么装什么，不像 Django 一股脑全给你。
