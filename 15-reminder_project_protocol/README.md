# 叮叮提醒 — 协议接口详解

> 项目使用的 AI Pet 远程服务器 HTTP 与 WebSocket 协议完整说明。
> 包含所有调用的接口、参数、数据格式和业务流程。

---

## 目录

1. [系统架构总览](#1-系统架构总览)
2. [HTTP 协议接口](#2-http-协议接口)
3. [WebSocket 协议接口](#3-websocket-协议接口)
4. [完整业务流程](#4-完整业务流程)

---

## 1. 系统架构总览

```
┌──────────────────────────────────────────────────────────────────┐
│                        电脑端                                     │
│  ┌──────────────────┐    ┌──────────────────┐                    │
│  │ 8000 端口          │    │ 8001 端口          │                    │
│  │ 主界面 + 调度器    │    │ 管理端 HTTP 代理   │                    │
│  │ 本地提醒 + SSH     │    │ 创建/查询/删除     │                    │
│  └──────────────────┘    └─────────┬──────────┘                    │
│                                      │ HTTP /api/v1                 │
│                                      ▼                             │
│                        ┌──────────────────────────┐                │
│                        │  AI Pet 远程服务器          │                │
│                        │  47.118.26.156:8000       │                │
│                        │  MySQL: ai_pet_reminders  │                │
│                        └────┬─────────────────────┘                │
│                             │ WebSocket                            │
│                             ▼                                      │
│                        ┌──────────────────────────┐                │
│                        │  RK3576 板子               │                │
│                        │  192.168.1.160            │                │
│                        │  board_ws_client.py        │                │
│                        │  Flask API + SQLite       │                │
│                        └──────────────────────────┘                │
└──────────────────────────────────────────────────────────────────┘
```

## 2. HTTP 协议接口

所有 HTTP 接口基路径：`` http://47.118.26.156:8000/api/v1 ``
认证方式：`` Authorization: Bearer {token} ``

### 2.1 登录认证

#### 2.1.1 手机号短信登录 (Section 2.1)

```
GET /aipet/app/auth/{phone_number}/{sms_code}
```

使用示例：
```
GET /aipet/app/auth/13900139000/888888
```

参数：
| 参数 | 值 | 说明 |
|------|------|------|
| phone_number | 13900139000 | 用户手机号 |
| sms_code | 888888 | 硬编码测试验证码 |

返回：
```json
{
  "code": 200,
  "msg": "请求成功",
  "data": "eyJhbGciOiJIUzI1NiIs...",
  "success": true
}
```

JWT Payload：
```json
{
  "user_id": 41,
  "phone_number": "13900139000",
  "session_id": "2499b103-...",
  "exp": 1782460800
}
```

#### 2.1.2 获取我的信息 (Section 2.5)

```
GET /aipet/app/myinfo
```

用途：8001 的 `` refresh() `` 函数在 token 缓存超过 5 分钟后调用此接口检测有效性。

### 2.2 宠物管理

#### 2.2.1 绑定宠物 (Section 2.2)

```
GET /aipet/app/bind/{serial_number}
```

#### 2.2.2 解绑宠物 (Section 2.3)

```
GET /aipet/app/unbind/{serial_number}
```

#### 2.2.3 我的宠物列表 (Section 2.4)

```
GET /aipet/app/myaipets
```

返回当前用户的宠物列表，8001 用 `` get_pid() `` 获取 `` pet_id ``。

#### 2.2.4 宠物状态 (Section 2.6)

```
GET /aipet/app/status/{aipet_id}
```

### 2.3 提醒 CRUD (Section 22)

#### 2.3.1 提醒列表 (Section 22.1)

```
GET /aipet/app/reminders/list/{aipet_id}/{page_num}/{page_size}
```

返回字段说明：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 记录 ID |
| title | string | 提醒标题 |
| content | string | 提醒内容 |
| reminderTime | datetime | 触发时间 |
| repeatType | string | 重复类型 (none/daily/weekly/monthly) |
| status | string | pending/sent/executing/completed/failed/cancelled |
| deliveryId | string | 新协议：下发追踪 ID |
| deliveryParams | dict | 新协议：下发参数 |
| result | dict | 设备执行结果 |
| sentTime | datetime | 指令下发时间 |
| executedTime | datetime | 执行完成时间 |

状态枚举：
```
pending   -> 待下发    (板子离线)
sent      -> 已下发    (板子在线)
executing -> 执行中    (时间到+没人)
completed -> 已完成    (播放完成)
failed    -> 失败      (超1小时无人)
cancelled -> 已取消    (远程取消)
```

#### 2.3.2 新增提醒 (Section 22.3)

```
POST /aipet/app/reminders/{aipet_id}
```

请求体：
```json
{
  "title": "小明，记得去拖地",
  "content": "小明，记得去拖地",
  "reminderTime": "2026-06-24T17:21:00",
  "repeatType": "none"
}
```

新协议行为：创建即自动下发，无需再调独立发送端点。

旧协议 vs 新协议：
- 旧协议：需要两步（创建 + 单独调用发送端点 Section 22.6）
- 新协议：一步到位，创建即自动下发

#### 2.3.3 编辑提醒 (Section 22.4)

```
PUT /aipet/app/reminders/{reminder_id}
```

请求体（只需传要修改的字段）：
```json
{ "status": "completed", "sentTime": "2026-06-24T15:25:32" }
```

#### 2.3.4 删除提醒 (Section 22.5)

```
DELETE /aipet/app/reminders/{reminder_ids}
```

### 2.4 WebSocket 辅助接口

#### 2.4.1 获取 WS 认证 Token

```
GET /aipet/ws/auth/{serial_number}
```

板子 `` board_ws_client.py `` 连接 WS 前用此接口获取 JWT Token。

### 2.5 本地 API (8000 后端)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/reminders | 本地提醒列表 |
| POST | /api/reminders | 创建本地提醒 |
| GET | /api/board-reminders | 获取板子提醒 |
| GET | /api/board-reminders/status | 板子在线状态 |
| POST | /api/board-reminders/sync | 同步提醒到缓存 |
| POST | /api/board-reminders/status-update | 更新状态 (SSH同步板子) |
| POST | /api/board-reminders/delete-record | 物理删除板子记录 |

### 2.6 管理端 API (8001 服务器)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/board-status | 板子在线检测 (socket) |
| POST | /api/send-reminder | 创建并下发提醒 |
| GET | /api/remote-reminders | 远程服务器提醒列表 |
| POST | /api/update-remote-status | 更新远程提醒状态 |
| POST | /api/cancel-remote-reminder | 取消提醒 (cancelled) |
| POST | /api/delete-remote-reminder | 删除远程提醒 |
| POST | /api/delete-remote-reminder-record | 删除远程+板子物理删除 |

## 3. WebSocket 协议接口

### 3.1 连接与认证

板子连接地址：
```
ws://47.118.26.156:8000/api/v1/aipet/ws/6976f96f-bc80-56e3-9b27-13d12cdde9d3
```

认证流程：
1. 板子发送：`` { "type": "auth", "access_token": "ws_jwt_token..." } ``
2. 服务器回复：`` { "type": "auth", "success": true } ``

### 3.2 下行消息 (服务器 -> 板子)

#### 3.2.1 reminder_delivery (Section 4.2，当前唯一通道)

```json
{
  "type": "reminder_delivery",
  "reminder_id": "rmd_3_1782292760_-6372849116477353038",
  "reminder_data": {
    "title": "小明，记得去拖地",
    "content": "小明，记得去拖地",
    "reminder_time": "2026-06-24T17:21:00",
    "repeat_type": "none"
  },
  "reminder_source": "app_chat",
  "priority": "high"
}
```

板子处理流程：
```
收到 reminder_delivery
  -> _handle_reminder_delivery()
  -> insert_reminder(reminder_id, reminder_data)
  -> SQLite INSERT (status=pending, command_id=reminder_id)
  -> 发送 reminder_response {status: "executing"}
```

#### 3.2.2 server_command (旧协议回退)

```json
{
  "type": "server_command",
  "command_id": "cmd_3_1718800000_abc123",
  "command": "reminder",
  "command_params": { "reminder_data": { ... }, "reminder_source": "app_chat" }
}
```

注：当前日志确认从未收到此类型。

### 3.3 上行消息 (板子 -> 服务器)

#### 3.3.1 初始回报 (收到后立即回复)

```json
{
  "type": "reminder_response",
  "reminder_id": "rmd_3_1782292760_-6372849116477353038",
  "status": "executing",
  "result": {
    "received": true,
    "board_id": 11374,
    "status": "executing"
  },
  "error": null
}
```

#### 3.3.2 状态变更回报 (轮询线程)

```json
{
  "type": "reminder_response",
  "reminder_id": "rmd_3_1782292760_-6372849116477353038",
  "status": "completed",
  "result": {
    "board_id": 11374,
    "content": "小明，记得去拖地",
    "reminder_time": "2026-06-24T17:21:00",
    "status": "completed"
  }
}
```

发送时机：`` _poll_status_changes() `` 每 10 秒检查 SQLite，发现 status 变为 completed/failed/cancelled 且 reported=0 时发送。

### 3.4 新旧协议对比

| 对比项 | 旧协议 | 新协议 |
|--------|--------|--------|
| 下发消息类型 | server_command (含 reminder) | reminder_delivery (独立) |
| 回报消息类型 | command_response | reminder_response |
| ID 字段名 | command_id | reminder_id |
| 参数字段名 | command_params | reminder_data (顶层) |
| 下发函数 | send_command_to_aipet() | send_reminder_to_aipet() |
| 写日志表 | 写 ai_pet_command_logs | 不写 |
| Handler | CommandResponseMessageHandler | ReminderResponseMessageHandler |
| ID 格式前缀 | cmd_ | rmd_ |

## 4. 完整业务流程

### 4.1 发送提醒

```
用户点击发送
  -> 8001 send_reminder()
  -> refresh() 验证/获取 token
  -> get_pid() 获取 pet_id=3
  -> POST /reminders/3 (Section 22.3)
     -> 远程服务器 INSERT (status=pending)
     -> 远程服务器自动 send_reminder_to_aipet()
     -> WS reminder_delivery -> 板子
     -> 板子回复 reminder_response {status:executing}
     -> 服务器 UPDATE status=sent, sent_time, delivery_id
  -> 检测板子是否在线
     -> 在线: PUT {status:sent, sentTime:now}
     -> 离线: PUT {status:pending}
  -> 直连板子 Flask POST /api/reminders/create
  -> 同步到 8000 缓存 POST /sync
  -> 用户看到 "已发送"
```

### 4.2 板子接收提醒

接收路径有两条：

路径A (WS新协议)：
```
远程服务器 -> WS reminder_delivery
  -> board_ws_client.on_message()
  -> _handle_reminder_delivery()
  -> insert_reminder() -> SQLite INSERT (command_id=rmd_3_...)
  -> 回复 reminder_response {status:executing}
```

路径B (直连Flask)：
```
8001 -> POST /api/reminders/create
  -> 板子 Flask run.py -> SQLite INSERT (command_id=NULL)
```

两条路径同时工作，导致板子上同一条提醒出现两条记录。

### 4.3 8000 调度器自动播报

```
调度器每 5 秒 -> process_reminders()
  -> 读取 board_reminders.json
  -> 对每条 status in [received, pending, sent, executing]:

     时间未到 -> 跳过

     时间到 + 有人 -> TTS 合成 -> 播放
        status -> completed
        SSH 更新板子 SQLite
        通知远程服务器

     时间到 + 没人 -> status -> executing
        presence_delay_count +1
        10 分钟后重试

     超 1 小时无人 -> status -> failed
        SSH 同步 + 通知远程
```

### 4.4 取消与删除

取消 (仅限未完成提醒)：
```
用户点击取消
  -> PUT /reminders/{id} {status:cancelled}
  -> 8000 status-update -> SSH 更新板子 cancelled
```

删除 (永久删除)：
```
用户点击删除
  -> DELETE /reminders/{ids} (软删除)
  -> 8000 delete-record -> SSH 删除板子记录
```

---

> 文档版本 v2.0 -- 2026-06-25
> 对应新协议：AI-Pet-App-HTTP-API-协议文档(2).md、AI-Pet-WebSocket-协议文档(2).md
