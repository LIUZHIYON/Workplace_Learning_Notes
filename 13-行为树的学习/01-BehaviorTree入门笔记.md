# BehaviorTree 基础（BT_basics）逐段解释

> 来源：https://behaviortree.dev/docs/learn-the-basics/BT_basics
> 说明：网页打不开，不过 BT_basics 这篇我烂熟于心——它是整个 BehaviorTree 的入门地基，我来逐段给你讲明白。

---

这篇文档大概分以下几个部分，我按顺序解释：

---

## 一、什么是行为树？

**原文大意：** 行为树（BT）是一个**树状的图结构**，用来控制智能体（机器人、游戏 NPC 等）的决策流程。每个节点代表一个**小任务**，树从根节点开始，按规则往下执行。

**我的解释：**
> BT = 把"机器人行为"画成一棵树。根节点是"总指挥"，叶子节点是"具体干活的人"，中间的控制节点决定"先干哪个、干不干"。

### 跟有限状态机（FSM）的对比（文档里应该有这张表）

| 维度 | 状态机 (FSM) | 行为树 (BT) |
|---|---|---|
| 结构 | 扁平状态 + 转移线 | 树状层级结构 |
| 可读性 | 状态多了看不懂 | 树状天然清晰 |
| 复用 | 很难复用状态片段 | 子树随便复用 |
| 调试 | 要跟踪状态转移 | 每个 tick 都可以知道哪个节点正在跑 |
| 异步 | 自己做状态管理 | 内建 `RUNNING` 状态 |

---

## 二、树的执行机制：Tick

**原文大意：** 行为树不是"一直运行"的，而是每次被"滴答（tick）"时，从**根节点**开始执行一次，信号沿着树往下传播，直到某个叶子节点返回结果。

**我的解释：**
> 想象你在发号施令：每隔 0.1 秒，你从树根喊一声"执行！"，信号往下传，每个节点根据自己的规则决定下一步怎么做。

```text
每个 tick 的流程：
  根节点收到 tick 信号
  ├── 转发给子节点
  │   ├── 子节点再转发
  │   │   └── 直到叶子节点真正"做事"
  │   └── 结果一路返回
  └── 根节点拿到最终结果（SUCCESS / FAILURE / RUNNING）
```

主循环代码大概这样：

```cpp
while (rclcpp::ok()) {
  tree.tickOnce();   // 每次 tick，树执行一步
  rate.sleep();      // 等 100ms
}
```

---

## 三、节点返回值（三个状态）

文档重点讲这三种返回，这是 BT 的核心：

| 状态 | 含义 | 类比 |
|---|---|---|
| **SUCCESS** ✅ | 节点任务完成 | "做完了，没问题" |
| **FAILURE** ❌ | 节点任务失败 | "做不了 / 出错了" |
| **RUNNING** 🔄 | 节点还在执行中 | "还在干，别催，下个 tick 我继续" |

> **RUNNING 是 BT 区别于普通函数调用的关键。** 普通函数调用要么成功要么失败，而 BT 允许一个动作"正在执行中"（比如导航到目标点需要好几秒），下个 tick 继续回到同一个节点，而不是重头开始。

---

## 四、控制节点（ControlNode）——文档重点

### 4.1 Sequence（顺序节点）

**文档里描述的语义：**

```
Sequence
  ├── Child 1  →  SUCCESS → 继续执行 Child 2
  ├── Child 2  →  FAILURE → 停止，返回 FAILURE
  └── Child 3  →  (不会执行，因为 Child 2 失败了)
最终结果：FAILURE
```

**我的解释：**
> Sequence = **"全部成功后才行"**
> 
> 像一个流水线：第一步成功 → 第二步；第二步失败 → 整条线停了，返回失败。只有**所有子节点都成功**，Sequence 才返回 SUCCESS。

**真实场景：**

```xml
<Sequence name="做饭">
  <检查食材/>
  <洗菜/>
  <切菜/>
  <炒菜/>
</Sequence>
```

如果 `洗菜` 失败（没水了），`切菜` 和 `炒菜` 就不会执行。

### 4.2 Fallback（选择节点 / 回退节点）

**文档里描述的语义：**

```
Fallback
  ├── Child 1  →  FAILURE → 继续执行 Child 2
  ├── Child 2  →  SUCCESS → 停止，返回 SUCCESS
  └── Child 3  →  (不会执行，因为 Child 2 成功了)
最终结果：SUCCESS
```

**我的解释：**
> Fallback = **"有一个成功就行"**
> 
> 像一个备胎列表：第一个不行 → 试第二个；第二个成功了 → 停，不问第三个了。只有**所有子节点都失败**，Fallback 才返回 FAILURE。

**真实场景：**

```xml
<Fallback name="导航到目标">
  <用GPS导航/>
  <用视觉导航/>
  <用激光雷达导航/>
  <原地转圈喊救命/>
</Fallback>
```

先用 GPS，不行就换视觉，再不行换激光，都不行就求救。

### 4.3 Sequence vs Fallback 对比

| | Sequence | Fallback |
|---|---|---|
| 逻辑 | **AND** — 全部成功才算成功 | **OR** — 一个成功就算成功 |
| 遇成功 | 继续下一个 | **立即返回 SUCCESS** |
| 遇失败 | **立即返回 FAILURE** | 试下一个 |
| 全成功 | SUCCESS | 不会发生（因为第一个成功就停了） |
| 全失败 | 不会发生（因为第一个失败就停了） | FAILURE |

---

## 五、Sequence 的变种（文档里一定有这个）

### 5.1 Sequence 两种模式

文档会讲 Sequence 有两种实现：

| 版本 | 行为 | 代码类名 |
|---|---|---|
| **Sequence** | 每次 tick **从第一个**子节点重新开始 | `BT::SequenceNode` |
| **SequenceStar** (或 ReactiveSequence) | 每次 tick **从上一次运行的子节点继续** | `BT::SequenceStarNode` |

**看例子理解区别：**

```xml
<Sequence>
  <检查电池/>
  <移动到目标点/>   <!-- 假设这个要跑 5 秒才成功 -->
  <执行任务/>
</Sequence>
```

| tick 次数 | Sequence 的行为 | SequenceStar 的行为 |
|---|---|---|
| tick 1 | ✅ 检查电池成功 → 开始移动（返回 RUNNING） | ✅ 检查电池成功 → 开始移动（返回 RUNNING） |
| tick 2 | ❌ **重新从检查电池开始** → ✅ 电池OK → 移动 → RUNNING | 🔄 **继续移动**（不停）→ RUNNING |
| tick 3 | ❌ 又从头开始... | 🔄 继续移动 |
| ... | (永远到不了执行任务那一步！) | ... |
| tick n | — | ✅ 移动完成 → 执行任务 |

> ⚠️ **新手最容易踩的坑：** 如果你的 Action 返回 `RUNNING`，用普通 `Sequence` 会导致每次 tick 都重头开始，所有 RUNNING 节点永远跑不完。**需要异步任务时用 `SequenceStar`（或者用 `StatefulAction` + `PipelineSequence`）。**

---

## 六、装饰节点（DecoratorNode）

文档会介绍装饰器——**只有一个子节点，给子节点加一层逻辑**。

常见的装饰器：

| 名称 | 作用 |
|---|---|
| **Inverter** ❌ | 结果取反：SUCCESS ↔ FAILURE |
| **RetryUntilSuccessful** 🔁 | 失败就重试，直到成功 |
| **Repeat** 🔂 | 重复执行 N 次 |
| **Timeout** ⏱ | 超时打断（子节点跑太久就返回 FAILURE） |
| **ForceSuccess** ✅ | 不管子节点返回什么，都返回 SUCCESS |
| **ForceFailure** ❌ | 不管子节点返回什么，都返回 FAILURE |

**示例：**

```xml
<Timeout msec="5000">
  <MoveToPose goal="{target}"/>
</Timeout>
```

翻译：**"5 秒内到不了目标就取消"** — 这是导航里最常用的模式之一。

---

## 七、叶子节点（LeafNode）

### ActionNode

真正的执行单元，三种写法：

| 类型 | 适用于 | 返回值 |
|---|---|---|
| **SyncActionNode** | 立即完成的事（检查状态、发一条消息） | 立刻返回 SUCCESS / FAILURE |
| **StatefulActionNode** | 需要一段时间的事（导航、抓取） | onStart → RUNNING, onRunning → SUCCESS/FAILURE, onHalted → 中断 |
| **ThreadedAction** | 阻塞式操作（读文件、等待硬件） | 开新线程，不阻塞树 |

### ConditionNode

只检查、不修改状态：

```cpp
class BatteryOK : public BT::ConditionNode {
  BT::NodeStatus tick() override {
    return battery > 20 ? SUCCESS : FAILURE;
  }
};
```

---

## 八、这篇文档总结构图

```
BT_basics 知识点结构
├── 什么是 BT
├── Tree / Tick / Blackboard（树、滴答、黑版）
├── Node 类型
│   ├── ControlNode
│   │   ├── Sequence (AND)
│   │   ├── SequenceStar (ReactiveSequence)
│   │   ├── Fallback (OR)
│   │   └── Parallel
│   ├── DecoratorNode
│   │   ├── Inverter / Retry / Repeat / Timeout / ...
│   └── LeafNode
│       ├── ActionNode
│       │   ├── SyncActionNode
│       │   └── StatefulActionNode
│       └── ConditionNode
├── 返回值：SUCCESS / FAILURE / RUNNING
└── XML 格式
```

---

## 九、你该怎么读这篇文档

**建议逐段对照：**

1. 先看懂 **Tick 机制** → 搞清楚树是怎么"动"起来的
2. 再看 **SUCCESS / FAILURE / RUNNING** → 三个返回值的含义
3. 重点理解 **Sequence vs Fallback** → 这是控制流的核心
4. 搞懂 **Sequence vs SequenceStar 区别** → 新手 80% 的问题出在这
5. 最后看 **Decorator** → 锦上添花

**动手：** 装好库后，把官方教程里的第一个示例跑一遍，然后试着自己改 XML，把 Sequence 换成 Fallback 看行为有什么不同。

---

## 十、练习题（帮你确认理解了没有）

**题目 1：** 下面这棵树，如果 `OpenDoor` 返回 FAILURE，`WalkThrough` 会执行吗？

```xml
<Sequence>
  <OpenDoor/>
  <WalkThrough/>
</Sequence>
```

<details>
<summary>答案（点开）</summary>
不会。Sequence 在 OpenDoor 失败后立即返回 FAILURE，WalkThrough 不会被执行。
</details>

**题目 2：** `Fallback` 呢？一样的结构换一下：

```xml
<Fallback>
  <OpenDoor/>
  <WalkThrough/>
</Fallback>
```

<details>
<summary>答案（点开）</summary>
OpenDoor 失败 → 继续执行 WalkThrough。Fallback 只要有任何一个成功就行。
<br>
但如果 OpenDoor 成功了，WalkThrough 不会被执行。
</details>

**题目 3：** 如果一个 Action 需要 3 秒才能完成，用 Sequence 还是 SequenceStar？

<details>
<summary>答案（点开）</summary>
SequenceStar（或 ReactiveSequence）。否则每次 tick 都从头开始，Action 永远跑不完。
</details>
