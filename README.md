# 📚 Workplace Learning Notes

> 工作中积累的技术学习笔记，涵盖 AI、机器人、版本控制、计算机视觉等领域。

---

## 📖 笔记目录

| # | 分类 | 笔记 | 简介 | 配图 |
|---|:----:|------|------|:----:|
| 1 | 🤖 | **[AI Agent 学习笔记](./01-AI-Agent/AI%20Agent%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0.md)** | Agent 核心架构、ReAct 循环、主流框架对比 | 🖼️ 2 张 |
| 2 | 🔌 | **[MCP 学习笔记](./02-MCP/MCP%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0.md)** | MCP 协议详解、生命周期流程、代码实践 | 🖼️ 2 张 |
| 3 | 📚 | **[Git 学习笔记](./03-Git/Git%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0.md)** | Git 工作流、分支模型、常用命令、协作流程 | 🖼️ 2 张 |
| 4 | 🤖 | **[ROS2 学习笔记](./04-ROS2/ROS2%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0.md)** | ROS2 架构、通信模型、开发实践 | 🖼️ 2 张 |
| 5 | 🗺️ | **[Nav2 学习笔记](./05-Nav2/Nav2%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0.md)** | Nav2 导航架构、行为树、配置调参 | 🖼️ 2 张 |
| 6 | 🌙 | **[低光照增强与分割](./06-低光照增强与分割/低光照增强与分割方案汇总.md)** | 低光照地板/墙壁分割四大方案汇总 | 🖼️ 2 张 |
| 7 | 📄 | **[低光照增强论文精读](./07-低光照增强论文精读/低光照增强论文精读_KSCE2025.md)** | KSCE 2025 论文精读：6种增强方法评估 | 🖼️ 2 张 |

---

## 🗂️ 文件结构

```
├── README.md                        # 项目说明
│
├── 📁 01-AI-Agent/                  # 🤖 AI Agent
│   ├── AI Agent学习笔记.md
│   ├── ai_agent_architecture.svg    # 核心架构图
│   └── react_loop.svg               # ReAct 循环图
│
├── 📁 02-MCP/                       # 🔌 MCP 协议
│   ├── MCP学习笔记.md
│   ├── mcp_architecture.svg         # 协议架构图
│   └── mcp_protocol_flow.svg        # 交互流程图
│
├── 📁 03-Git/                       # 📚 Git 版本控制
│   ├── Git学习笔记.md
│   ├── git_workflow.svg             # 工作流图
│   └── git_branching.svg            # 分支模型图
│
├── 📁 04-ROS2/                      # 🤖 ROS2 机器人
│   ├── ROS2学习笔记.md
│   ├── ros2_architecture.svg        # 整体架构图
│   └── ros2_communication.svg       # 通信模型图
│
├── 📁 05-Nav2/                      # 🗺️ Nav2 导航
│   ├── Nav2学习笔记.md
│   ├── nav2_architecture.svg        # 导航架构图
│   └── nav2_bt.svg                  # 行为树图
│
└── 📁 06-低光照增强与分割/          # 🌙 低光照增强与分割
    ├── 低光照增强与分割方案汇总.md
    ├── overview_pipeline.svg        # 整体方案分类图
    └── clahe_diagram.svg            # CLAHE 原理图
│
└── 📁 07-低光照增强论文精读/          # 📄 KSCE 2025 论文精读
    ├── 低光照增强论文精读_KSCE2025.md
    ├── experiment_pipeline.svg      # 实验流程设计
    └── methods_overview.svg         # 六种方法架构总览图
```

---

## 🎯 内容速览

### 01 — 🤖 AI Agent

```
核心架构 → ReAct 循环 → Agent 分类 → 关键组件（记忆/工具/规划）→ 框架对比（7 种）
```

### 02 — 🔌 MCP (Model Context Protocol)

```
为什么需要 MCP → 三层架构（Host/Client/Server）→ 生命周期 → 
三大概念（Resources/Tools/Prompts）→ JSON-RPC → 代码实践
```

### 03 — 📚 Git

```
四大区域 → 分支模型（Git Flow / GitHub Flow）→ 命令速查 → 
Merge vs Rebase → 协作流程 → .gitignore → 进阶技巧
```

### 04 — 🤖 ROS2

```
ROS1 vs ROS2 → 分层架构 → 核心概念（Node/Topic/Service/Action）→ 
通信模型详解 → Package 结构 → Launch → 生命周期管理
```

### 05 — 🗺️ Nav2

```
系统架构 → BT Navigator → 代价地图 → 规划器 → 控制器 → 
行为树详解 → 配置调参 → 常见问题排查
```

### 06 — 🌙 低光照增强与分割

```
四大方案（传统/深度学习/端到端/多模态）→ CLAHE → Zero-DCE → SCI → 
RGB-D 融合 → 效果对比 → 按硬件条件推荐方案
```

---

## 📝 说明

- 笔记使用 **Markdown** 编写，内含 **SVG 架构图/流程图**
- 推荐用 **Typora**、**VS Code**、**Obsidian** 等支持图片渲染的编辑器打开
- 各笔记末尾附有学习心得
- 持续更新中 🚧

---

## 📄 License

MIT
