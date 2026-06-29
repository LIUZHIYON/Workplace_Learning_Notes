# Groot2 ZMQ 连接调试记录

> 时间：2026-06-29
> 板子 IP：192.168.1.191
> 相关仓库：[reminder_codex](http://42.121.217.40:3000/openclaw-lzy/reminder_bt)
> 监视器：`E:\LuBanCat\BT_ros2\BehaviorTreeMonitor`

---

## 问题 1：行为树监视器连不上板子

**小夏（提问）：** 192.168.1.191这是我的板子ip，账号cat，密码temppwd，板子上面有一个提醒行为树节点在运行，但是我的E:\LuBanCat\BT_ros2\BehaviorTreeMonitor 这个行为树监视器连接不上，帮我查询一下原因，不要修改代码

---

**小夏（回答）：** 找到了！排查结果如下：

---

## 诊断结果：ZMQ 帧格式不匹配

**网络层面一切正常 ✅**
- 端口 1667 (ZMQ)：**通**
- 端口 1668 (ZMQ PUB)：**通**
- 我用 ZMQ REQ 从 Windows 连板子发 FULLTREE 请求，**成功返回了行为树 XML**（收到了 584 字节的有效数据）

**根本原因：单帧 vs 多帧协议不一致**

**板子端** (`groot2_server_v2.py`) 的 ZMQ 发送：
```python
sock = ctx.socket(zmq.REP)
sock.send(reply)  # ← 单帧发送，header+uuid+内容都塞在一个ZMQ帧里
```

**BehaviorTreeMonitor** (`server.py`) 的 ZMQ 接收：
```python
await self.zmq_socket.send_multipart([header, b''])  # 发送2帧
reply = await self.zmq_socket.recv_multipart()         # 期望收到≥2帧
if reply and len(reply) >= 2:                          # ← 实际只有1帧，永远为False
```

**数据验证：**
```
我发出的请求:  send_multipart([6字节header, b'']) → 2帧
收到的回复:    1个frame (584 bytes)，里面包含 header(6)+uuid(16)+长度(4)+XML(558)
```

所以 monitor 收到 1 帧时 `len(reply)=1 < 2`，`_request_tree()` 直接返回 `None`，`connect_zmq()` 就报连接失败。

**修复方向（两选一）：**

**方案 A - 改板子端**（`groot2_server_v2.py` 第 82 行附近）：
```python
# 把 send(reply) 换成 send_multipart 分两帧发
header_part = reply[:22]      # protocol + type + uid + uuid
content_part = reply[26:]      # 跳过长度字段
sock.send_multipart([header_part, content_part])
```

**方案 B - 改 Monitor 端**（`server.py` 的 `_request_tree/send_request`）：
```python
# 收1帧时解析兼容单帧格式
reply = await self.zmq_socket.recv_multipart()
if reply and len(reply) >= 1:
    # 兼容单帧格式：reply[0] 包含 header + uuid + content_len + content
```

不改代码的话，目前就是连接不上的状态。要修哪个端？

---

## 问题 2：连接失败 — 端口 1669

**小夏（提问）：** 我现在主要是这个问题
连接失败
连接超时或对端未响应: tcp://192.168.1.191:1669
可以解决吗？

---

**小夏（回答）：** 清楚了！问题有两个层面：

---

## 诊断结果

### 1️⃣ 端口号填错了

你在 Monitor 里填了 **1669**，但板子上的 ZMQ 服务开在 **1667**。两个端口我都测试过：

| 端口 | 状态 | 内容 |
|------|------|------|
| **1667** | ✅ 通 | 行为树 v2 |
| **1669** | ✅ 通（但写法不同，应该是另一个脚本） | 行为树 v1 |
| **1668** | ✅ 通 | 黑板事件 PUB |

→ **在 Monitor 的 UI 里把端口改成 `1667`**

### 2️⃣ ZMQ 帧格式不匹配（核心问题）

就算连对端口也连不上，因为：

**板子端** (`groot2_server_v2.py`) 用单帧发：
```python
sock.send(reply)  # 所有数据塞在一个 ZMQ 帧里
```

**Monitor 端** (`server.py`) 用多帧收：
```python
reply = zmq_socket.recv_multipart()
if len(reply) >= 2:  # 收到 1 帧，条件永远不成立
```

我已经验证过：Monitor 发出的 FULLTREE 请求，板子正常返回了 XML 数据，但因为只有 **1 个 ZMQ 帧**，Monitor 的 `len(reply) >= 2` 判断失败，直接报"连接超时或对端未响应"。

---

**修复方案**（需要改板子端的代码，不改 Monitor）：

编辑板子上的 `groot2_server_v2.py`，把第 82 行左右的 `sock.send(reply)` 改成多帧发送：

```python
# 修改前
sock.send(reply)

# 修改后
header_part = reply[:22]         # 协议头(6) + UUID(16)
content_part = reply[26:]        # 跳过4字节长度字段
sock.send_multipart([header_part, content_part])
```

STATUS 回复那里的 `sock.send(reply)` 也同样处理。

要这样改吗？

---

## 问题 3：连上后显示异常（UID 重复 & 黑板为空）

**小夏（提问）：** 
```
10IDLE
2RUNNING
3SUCCESS
2FAILURE
黑板 0 keys / 全部 1 keys
_raw:int123
```
这对吗？

---

**小夏（回答）：** 不对，主要有两个问题：

**1. 节点状态显示** - 基本能看，但有异常
```
10IDLE
2RUNNING
3SUCCESS
2FAILURE ← UID 2 出现了两次，一次 RUNNING 一次 FAILURE
```
说明板子上两个不同节点被分配了同一个 UID（`uid_counter` 可能没正确处理），这会导致状态显示错乱。

**2. 黑板显示** - 完全不对
```
黑板 0 keys / 全部 1 keys
_raw:int123
```

`groot2_server_v2.py` 里**没有处理 BLACKBOARD 请求**，只有 `T`(FULLTREE) 和 `S`(STATUS)：
```python
if req_type == ord('T'):
    ...  # FULLTREE 处理
elif req_type == ord('S'):
    ...  # STATUS 处理
else:
    # 黑板请求走到这里
    sock.send(空数据)  ← 返回空，Monitor 解析不了
```

所以黑板显示的 `_raw:int123` 是 Monitor 解析 MessagePack 失败后的 fallback 内容，不是真实的黑板数据。

**总结现状：**
| 功能 | 状态 |
|------|------|
| ZMQ 连接 | ✅ 已通（你改了 send_multipart？） |
| 树结构展示 | ✅ 基本正常 |
| **节点状态** | ⚠️ UID 有重复，需要修 |
| **黑板数据** | ❌ 缺 BLACKBOARD 处理器 |

要我把 board 备份里的 `groot2_server_v2.py` 修正一下，加上黑板处理 + 修复 UID 重复问题吗？

---

## 问题 4：连上了但状态"卡住"

**小夏（提问）：** 现在可以看见黑板的变量了，但是行为树节点的状态不是实时的变化，像卡住了一样

---

**小夏（回答）：** 找到原因了。问题出在 `groot2_server_v2.py` 里的黑板数据是**硬编码的假数据**：

```python
blackboard = {
    "blackboard_state": {"pending_count": 0, "is_playing": False},   # ← 永远没提醒
    "tts_feedback": {"status": None},                                 # ← 永远不 done
    "current_reminder": {},                                           # ← 空数据
    "tts_pub": lambda t: None,                                        # ← 空函数
    "cmd_pub": lambda d: None,                                        # ← 空函数
    "action_pub": lambda d: None,                                     # ← 空函数
}
```

**这个脚本是独立运行的，不连 ROS2 系统，所有数据都是死的：**

- `pending_count = 0` → `CheckPendingReminder` 永远返回 FAILURE
- 即使有提醒进来了，`tts_feedback.status = None` → `PlayAudio` 永远等不到 `"done"`，RUNNING 卡死
- 三个 `pub` 都是空函数，发不出任何真实消息

所以状态看起来是"卡住"了——实际上是没有真实数据驱动它变化。

---

**解决方案：要在板子上加一个真正连到 ROS2 系统的 ZMQ 桥接。**

有两条路可以走：

**方案 A：在 `reminder_bt_driver.py`（真正的 ROS2 节点）里直接嵌入 ZMQ 服务**

把 `groot2_server_v2.py` 的 ZMQ 逻辑搬到 `reminder_bt_driver.py` 里面，让它用真正的 ROS2 黑板数据而不是硬编码的假数据。

**方案 B：在 `groot2_server_v2.py` 里订阅 ROS2 话题更新黑板**

让 ZMQ 服务器订阅 ROS2 话题，把实时黑板状态同步进来。

你想走哪个方向？我可以直接改好代码。

---

## 问题 5：两个方案的区别

**小夏（提问）：** 两个方案有什么区别

---

**小夏（回答）：** 两者的区别主要在于**数据真实度**和**侵入性**：

---

## 方案 A：ZMQ 嵌入 ROS2 节点

```
┌─────────────────────────────────────┐
│  reminder_bt_driver.py              │
│  ┌──────────┐    ┌────────────────┐ │
│  │ BT 引擎   │◄──→│ ZMQ REP 服务   │ │
│  │ 真实数据  │    │ port 1667      │ │
│  └──────────┘    └──────┬─────────┘ │
│                         │            │
└─────────────────────────┼────────────┘
                          │ ZMQ
                    ┌─────▼──────┐
                    │ Monitor    │
                    └────────────┘
```

- ✅ 数据**100%实时**，直接读运行中的节点状态
- ✅ 不需要额外 `tree.tick_once()`——Status 请求时直接读当前帧的状态
- ✅ 黑板数据直接从 ROS2 的黑板拿
- ⚠️ 需要改 `reminder_bt_driver.py`（ROS2 节点代码）

## 方案 B：groot2_server 订阅 ROS2 话题

```
┌──────────────────┐    ┌──────────────────────┐
│ reminder_bt_     │    │ groot2_server_v2.py  │
│ driver.py (ROS2) │    │ ┌──── ZMQ REP ────┐  │
│   pub /tts/text  │    │ │ tree + 硬编码    │  │
│   pub /robot/... │    │ │ 黑板            │  │
│   sub blackboard │    │ └─────────────────┘  │
│   sub tts_fb     │    │    ▲ 订阅 ROS2 话题   │
└──────────────────┘    └────┼───────────────┘
      话题 pub/sub            │
                             │ ZMQ
                       ┌─────▼──────┐
                       │ Monitor    │
                       └────────────┘
```

- ✅ 和 ROS2 节点解耦，互不影响
- ❌ 需要订阅 3~4 个 ROS2 话题同步数据
- ❌ 数据有延迟（通过话题传递）
- ❌ 复杂：要多线程处理 rclpy + ZMQ
- ❌ 仍然需要 ROS2 环境

---

**我的建议：选方案 A**，原因很直接——

方案 A 就是在当前 ROS2 节点的 `_tick()` 循环里，每次 tick 后把节点状态记下来，开一个 ZMQ 端口让 Monitor 来读。**改动量很小**，数据也最准。方案 B 反而要搞话题订阅同步，麻烦多了。

要我按方案 A 改吗？
