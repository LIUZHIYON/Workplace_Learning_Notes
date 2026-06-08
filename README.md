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
| 6 | 🔬 | **[低光照处理专题](./06-低光照处理专题/README.md)** | 低光照图像处理全链路：增强、降噪、论文、分割预处理 | 🖼️ 多张 |
| 7 | 🖼️ | **[OpenCV 完整学习笔记](./07-OpenCV学习笔记/README.md)** | OpenCV 全模块指南：20个专题+流行度排行+配图 | 🖼️ 11 张 |
| 8 | 📝 | **[NLP 完整学习笔记](./08-NLP学习笔记/README.md)** | NLP全栈：传统方法→BERT/GPT→LLM→RAG→Agent→多模态 | 🖼️ 8 张 |
| 9 | 🎯 | **[Roboflow 学习笔记](./09-Roboflow学习笔记/README.md)**
| 10 | 🐳 | **[Docker 学习笔记](./10-Docker学习笔记/README.md)** | Docker全指南：容器/镜像/Compose/网络/卷/部署/RK3576 | 🖼️ 4 张 | | Roboflow全指南：数据集→标注→增强→合并→训练→部署 | 🖼️ 4 张 |
| 7 | 🖼️ | **[OpenCV 完整学习笔记](./07-OpenCV学习笔记/README.md)** | OpenCV 全模块指南：20个专题+流行度排行+配图 | 🖼️ 11 张 |
| 8 | 📝 | **[NLP 完整学习笔记](./08-NLP学习笔记/README.md)** | NLP全栈：传统方法→BERT/GPT→LLM→RAG→Agent→多模态 | 🖼️ 8 张 |
| 9 | 🎯 | **[Roboflow 学习笔记](./09-Roboflow学习笔记/README.md)**
| 10 | 🐳 | **[Docker 学习笔记](./10-Docker学习笔记/README.md)** | Docker全指南：容器/镜像/Compose/网络/卷/部署/RK3576 | 🖼️ 4 张 | | Roboflow全指南：数据集→标注→增强→合并→训练→部署 | 🖼️ 4 张 |

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
└── 📁 06-低光照处理专题/            # 🔬 低光照处理全链路
│
└── 📁 07-OpenCV学习笔记/              # 🖼️ OpenCV 完整指南
│
└── 📁 08-NLP学习笔记/                  # 📝 NLP 完整指南
│
└── 📁 09-Roboflow学习笔记/              # 🎯 Roboflow 完整指南
│
└── 📁 10-Docker学习笔记/                 # 🐳 Docker 完整指南
    ├── README.md                       # 18个专题完整笔记
    ├── gen_figures.py                  # 配图生成脚本
    ├── fig_vm_vs_docker.png            # VM vs Docker架构对比
    ├── fig_architecture.png            # Docker核心架构图
    ├── fig_dockerfile.png              # Dockerfile分层构建
    └── fig_network.png                 # 网络模式对比
    ├── README.md                       # 17个专题完整笔记
    ├── gen_figures.py                  # 配图生成脚本
    ├── fig_pipeline.png                # 完整工作流图
    ├── fig_merge.png                   # 数据集合并示意
    ├── fig_formats.png                 # 标注格式对比
    └── fig_deploy.png                  # 部署选项对比
    ├── README.md                       # 19个专题完整笔记
    ├── gen_figures.py                  # 配图生成脚本
    ├── fig_timeline.png                # NLP技术演进时间线
    ├── fig_transformer.png             # Transformer架构图
    ├── fig_model_size.png              # 模型参数规模对比
    ├── fig_frameworks.png              # 框架流行度排行
    ├── fig_rag.png                     # RAG架构图
    ├── fig_tasks.png                   # NLP任务流行度
    ├── fig_paradigms.png               # 微调范式对比
    └── fig_embedding.png               # 词嵌入可视化
    ├── README.md                       # 20个专题完整笔记
    ├── gen_figures.py                  # 配图生成脚本
    ├── fig_filter.png                  # 滤波对比图
    ├── fig_edge.png                    # 边缘检测
    ├── fig_threshold.png               # 阈值处理
    ├── fig_morph.png                   # 形态学操作
    ├── fig_hist.png                    # 直方图对比
    ├── fig_contour.png                 # 轮廓检测
    ├── fig_colorspace.png              # 色彩空间
    ├── fig_geo.png                     # 几何变换
    ├── fig_pyramid.png                 # 金字塔
    ├── fig_lowlight.png                # 低光照增强
    └── fig_dnn.png                     # DNN 流程
    ├── README.md                    # 专题总览
    │
    ├── 📁 01-低光照增强与分割方案汇总/   # 🌙 方案汇总
    │   ├── 低光照增强与分割方案汇总.md
    │   ├── overview_pipeline.svg
    │   ├── clahe_diagram.svg
    │   ├── low_light_tool.py
    │   └── low_light_gui.py
    │
    ├── 📁 02-低光照增强论文精读/        # 📄 论文精读
    │   ├── 低光照增强论文精读_KSCE2025.md
    │   ├── experiment_pipeline.svg
    │   └── methods_overview.svg
    │
    ├── 📁 03-OpenCV低光照处理方法/      # 🖼️ OpenCV 方法
    │   ├── README.md
    │   ├── generate_comparison.py
    │   ├── comparison_single_scene.png
    │   ├── comparison_single_portrait.png
    │   ├── comparison_combined_scene.png
    │   ├── comparison_combined_portrait.png
    │   └── histogram_comparison.png
    │
    └── 📁 04-低光照降噪与分割预处理/    # 🧹 降噪+分割预处理
        ├── README.md
        ├── generate_comparison.py
        ├── test_noisy_lowlight.png
        ├── comparison_denoise_only.png
        ├── comparison_edge_preservation.png
        ├── comparison_pipeline.png
        └── comparison_segmentation_preview.png
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

### 06 — 🔬 低光照处理专题

```
┌─ 01 低光照增强与分割方案汇总（传统/深度学习/端到端/多模态方案）
├─ 02 低光照增强论文精读（KSCE 2025 论文精读 + 6种方法评估）
├─ 03 OpenCV低光照处理方法（8种OpenCV方法对比 + 组合管线 + 效果图）
└─ 04 低光照降噪与分割预处理（6种降噪方法 + 增强管线 + RK3576性能估算）
│
└─ 07 OpenCV 完整学习笔记（全部20个模块 + 流行度排序 + 配图）
│
└─ 08 NLP 完整学习笔记（NLP全栈：传统→BERT/GPT→LLM→RAG→Agent→多模态）
```

---

## 📝 说明

- 笔记使用 **Markdown** 编写，内含 **SVG 架构图/流程图/对比图**
- 推荐用 **Typora**、**VS Code**、**Obsidian** 等支持图片渲染的编辑器打开
- 各笔记末尾附有学习心得
- 持续更新中 🚧

---

## 📄 License

MIT
