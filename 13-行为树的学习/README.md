# BehaviorTree.CPP 学习笔记

> 整理时间：2026-06-18  
> 涵盖版本：BT.CPP 4.x 官网文档（含 3.x → 4.x 迁移指南）  
> 共：**31 篇**笔记，覆盖官网 **100%** 文档内容

---

## 目录

- [关于本笔记](#关于本笔记)
- [笔记结构](#笔记结构)
- [如何阅读](#如何阅读)
- [快速参考](#快速参考)
- [资源地址](#资源地址)

---

## 关于本笔记

本文件夹包含 BehaviorTree.CPP 官方文档的**逐篇中文解释**，每一篇对应官网的一个页面。

每个 `.md` 文件的格式：
- 原文大意（官方说了什么）
- 我的解释（用人话翻译 + 例子 + 对比）

---

## 笔记结构

### 📖 Basic Concepts（概念篇）—— 01~03

先搞懂行为树是什么、怎么设计、XML 怎么写。

| # | 文件名 | 对应官网 |
|---|---|---|
| 01 | BehaviorTree入门笔记 | BT_basics |
| 02 | MainConcepts解释 | Main Concepts |
| 03 | XML格式解释 | XML schema |

### 🛠️ Tutorials Basic（基础教程）—— 04~14

从零开始写你的第一个行为树，到用 Groot2 可视化调试。

| # | 文件名 | 对应官网 |
|---|---|---|
| 04 | 第一棵行为树教程 | Tutorial 01 |
| 05 | 黑版和端口教程 | Tutorial 02 |
| 06 | 泛型端口教程 | Tutorial 03 |
| 07 | 响应式行为教程 | Tutorial 04 |
| 08 | 子树教程 | Tutorial 05 |
| 09 | 端口重映射教程 | Tutorial 06 |
| 10 | 多XML文件教程 | Tutorial 07 |
| 11 | 额外参数教程 | Tutorial 08 |
| 12 | 脚本语言教程 | Tutorial 09 |
| 13 | 观察者教程 | Tutorial 10 |
| 14 | Groot2连接教程 | Tutorial 11 |

### ⚡ Tutorials Advanced（高级教程）—— 15~19

默认端口值、零拷贝黑版访问、子树自动映射、Mock 测试、全局黑版。

| # | 文件名 | 对应官网 |
|---|---|---|
| 15 | 默认端口值教程 | Tutorial 12 |
| 16 | 零拷贝访问黑版教程 | Tutorial 13 |
| 17 | 子树模型和自动映射教程 | Tutorial 14 |
| 18 | Mock测试教程 | Tutorial 15 |
| 19 | 全局黑版教程 | Tutorial 16 |

### 📘 Guides（指南）—— 20~23

脚本语言参考、前置/后置条件、异步 Action、端口 vs 黑版设计哲学。

| # | 文件名 | 对应官网 |
|---|---|---|
| 20 | 脚本语言参考 | Scripting Guide |
| 21 | 前置后置条件指南 | Pre/Post Conditions |
| 22 | 异步动作指南 | Asynchronous Actions |
| 23 | 端口vs黑版指南 | Ports VS Blackboard |

### 📚 Nodes Library（节点库）—— 24~29

所有内置节点的完整行为参考。

| # | 文件名 | 对应官网 |
|---|---|---|
| 24 | 并行节点参考 | ParallelNode |
| 25 | 条件控制节点参考 | ConditionalControlNodes |
| 26 | Switch节点参考 | SwitchNode |
| 27 | 装饰器节点参考 | DecoratorNode |
| 28 | Fallback节点参考 | FallbackNode |
| 29 | Sequence节点参考 | SequenceNode |

### 🔌 集成与迁移 —— 30~31

| # | 文件名 | 对应官网 |
|---|---|---|
| 30 | ROS2集成指南 | ROS2 Integration |
| 31 | 升级迁移指南 | Migration from 3.x |

---

## 如何阅读

### 🆕 如果你是零基础

```
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14
```

看完这 14 篇，你就掌握了 BT.CPP 的**完整用法**。

### 🔧 如果你需要高级功能

继续看 15~19，按需查阅。

### 📖 如果你需要查节点行为

翻 24~29 的节点库参考。

### 🚀 如果你要在 ROS2 里用

翻 30。

---

## 快速参考

### 最核心的概念

| 概念 | 在哪篇 | 一句话 |
|---|---|---|
| Sequence / Fallback | 01 | AND / OR 逻辑 |
| Tick / RUNNING | 01、07 | 每次 tick 从根开始，异步 Action 返回 RUNNING |
| 黑版（Blackboard） | 05 | 节点之间共享数据的键值存储 |
| InputPort / OutputPort | 05 | 声明节点需要读/写什么数据 |
| ReactiveSequence | 07 | 每次 tick 重新检查第一个条件 |
| SubTree | 08 | 把一棵树嵌入另一棵树 |
| Port Remapping | 09 | 子树端口映射到父树黑版的 key |
| StatefulActionNode | 07、22 | 实现异步 Action 的推荐方式 |

### 常用的 Decorator

| Decorator | 作用 | 在哪篇 |
|---|---|---|
| Inverter | 取反 SUCCESS ↔ FAILURE | 08 |
| RetryUntilSuccessful | 失败时重试 N 次 | 08 |
| Timeout | 超时中断 | 07 |
| Precondition | 条件判断后执行 | 21 |
| RunOnce | 只执行一次 | 27 |
| Delay | 延迟后执行 | 27 |

---

## 资源地址

| 资源 | 地址 |
|---|---|
| 官网文档 | https://www.behaviortree.dev/ |
| 核心库 GitHub | https://github.com/BehaviorTree/BehaviorTree.CPP |
| ROS2 桥接 GitHub | https://github.com/BehaviorTree/BehaviorTree.ROS2 |
| Groot2 可视化 | https://github.com/BehaviorTree/Groot2 |
| Nav2 实战参考 | https://github.com/ros-planning/navigation2 |
| 该项目 GitHub | https://github.com/LIUZHIYON/Workplace_Learning_Notes |

---

*笔记整理：小夏 | 2026-06-18*
