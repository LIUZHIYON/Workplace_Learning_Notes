# Main Concepts 逐段解释

> 来源：https://behaviortree.dev/docs/learn-the-basics/main_concepts
> 说明：这篇是 BT_basics 的**进阶版**，讲的是 BehaviorTree.CPP 这个库的 5 个核心设计思想。

---

## 一、Nodes vs Trees（节点 vs 树）

**原文大意：**
> 用户只需要自己写 ActionNode 和 ConditionNode（叶子节点），库帮你把它们组装成树。叶子节点就像**乐高积木**，树就像用积木搭出来的模型。你的自定义节点应该是**高度可复用**的。

**我的解释：**

这个思想是 BT 的精髓——**C++ 写一次积木，XML 反复搭造型。**

```
你的工作：                   库帮你做的：
写一个个小积木                用 XML 搭成树

CheckBattery  ⟶  ◻           Sequence
MoveToGoal    ⟶  ◻             CheckBattery
SayHello      ⟶  ◻             MoveToGoal
                                 SayHello
```

换个场景，积木不用重写，换个 XML 就行：

```xml
<!-- 场景A：先检查再移动 -->
<Sequence>
  <CheckBattery/>
  <MoveToGoal/>
</Sequence>

<!-- 场景B：电池不行就充电，充完再移动 -->
<Fallback>
  <Sequence>
    <CheckBattery/>
    <MoveToGoal/>
  </Sequence>
  <Charge/>
</Fallback>
```

**一句话：** 叶子节点（C++）写一次，树结构（XML）随意换。

---

## 二、Instantiate trees at run-time using XML（运行时加载 XML）

**原文大意：**
> 虽然库是 C++ 写的，但树可以在**运行时**（更具体说是在**部署时**）用 XML 创建和组合。

**我的解释：**

这意味着**改机器人行为不用重新编译**。你把 XML 发给机器人，重启就行。

```cpp
// 编译一次，XML 随便换
int main() {
  BT::BehaviorTreeFactory factory;
  factory.registerNodeType<CheckBattery>("CheckBattery");
  factory.registerNodeType<MoveToGoal>("MoveToGoal");

  // 换 XML 文件就等于换行为，不用重新编译！
  auto tree = factory.createTreeFromFile("behavior_v1.xml");
  // auto tree = factory.createTreeFromFile("behavior_v2.xml");  // 换这个就行
}
```

**部署流程：**

```
开发机：
  写 C++ 节点 → 编译 → 注册到 factory
  写 XML 行为树

部署到机器人：
  传可执行文件（一次）
  传 XML（随时换，不用重编译）
```

---

## 三、The tick() callbacks（tick 回调机制）

**原文大意：**
> 任何一个 TreeNode 都可以看作是一个触发**回调**的机制——也就是**执行一段代码**。这段代码干什么由你决定。教程里简单起见只打印消息或 sleep，实际项目中 Action/Condition 通常会跟其他组件或服务通信。

**附带的代码示例：**

```cpp
// 最简单的回调：一个普通函数
NodeStatus HelloTick() {
  std::cout << "Hello World\n";
  return NodeStatus::SUCCESS;
}

// 注册到 factory，给这个回调起名叫 "Hello"
factory.registerSimpleAction("Hello", std::bind(HelloTick));
```

**我的解释：**

官方在强调一个设计模式——**tick() 不需要非得是类成员函数**。

| 方式 | 写法 | 适用场景 |
|---|---|---|
| **函数指针**（这篇教的） | `factory.registerSimpleAction("Name", func)` | 简单动作，几行代码 |
| **类继承**（下节讲的） | `class MyAction : public BT::SyncActionNode` | 复杂动作，需要成员变量 |

两种方式效果一样，选择取决于你的代码复杂度。

---

## 四、Create custom nodes with inheritance（用继承创建自定义节点）

**原文大意：**
> 上节用函数指针创建节点（依赖注入）。通用做法是从 TreeNode 或其子类继承。

三个可继承的基类：

| 基类 | 对应节点类型 | 用途 |
|---|---|---|
| `ActionNodeBase` | 动作节点 | 执行动作 |
| `ConditionNode` | 条件节点 | 检查条件 |
| `DecoratorNode` | 装饰节点 | 包装子节点 |

**我的解释：**

函数指针适合简单场景，但实际项目里大多用继承——因为你需要**状态、参数、ROS2 句柄**等成员变量。

```cpp
// 函数指针方式（简单）
NodeStatus HelloTick() { ... }
factory.registerSimpleAction("Hello", HelloTick);

// 继承方式（功能完整）
class HelloAction : public BT::SyncActionNode {
public:
  HelloAction(const std::string& name, const BT::NodeConfig& config)
    : BT::SyncActionNode(name, config) {
    // 这里可以初始化 ROS2 publisher 等
  }

  BT::NodeStatus tick() override {
    std::cout << "Hello from class!\n";
    return BT::NodeStatus::SUCCESS;
  }
};
factory.registerNodeType<HelloAction>("Hello");
```

**区别：**

| 维度 | 函数指针 | 继承 |
|---|---|---|
| 代码量 | 少 | 多一些 |
| 需要成员变量？ | ❌ 不方便 | ✅ 随便加 |
| 需要端口（ports）？ | ❌ 麻烦 | ✅ 标配 |
| 需要构造参数？ | ❌ 受限 | ✅ 灵活 |

---

## 五、Dataflow, Ports and Blackboard（数据流、端口和黑版）

**原文大意：**

> - **黑版（Blackboard）** 是一个树内所有节点共享的**键/值**存储。
> - **端口（Ports）** 是节点之间交换数据的机制。
> - 端口通过黑版的同一个 **key** 来"连接"。
> - 端口的数量、名字、类型在 **编译时**（C++）确定；端口之间的连接在 **部署时**（XML）完成。
> - 可以存储任意 C++ 类型（用了类似 `std::any` 的类型擦除技术）。

**我的解释：**

这是整个文档里**最重要的概念**。看例子：

**错误的做法：** 节点之间直接传数据

```cpp
// MoveTo 直接调用 SayHello——耦合了！
class MoveTo : public BT::SyncActionNode {
  SayHello& hello_;  // 强耦合！
};
```

**正确的做法：** 节点通过黑版交换数据

```xml
<Sequence>
  <DetectObject object="{detected_obj}"/>   <!-- 写入黑版 -->
  <GraspObject target="{detected_obj}"/>    <!-- 从黑版读取 -->
</Sequence>
```

执行流程：

```
          黑版 (Blackboard)
    ┌─────────────────────────┐
    │ "detected_obj" = bottle │  ← DetectObject 写入
    └─────────────────────────┘
              ↑        ↓
    DetectObject   GraspObject
    (写入端口)     (读取端口)
```

**端口 = 节点上的插孔，黑版 = 接线板：**

```
    DetectObject           GraspObject
    ┌──────────┐           ┌──────────┐
    │ object   │──输出────→│ (输出端) │
    │ (输出端) │           │ target   │
    └──────────┘           │ (输入端) │
          │                └────┬─────┘
          │                     │
          └──────────┬──────────┘
                     ↓
               {detected_obj}
              黑版上的同一个 key
```

**为什么编译时确定端口、运行时连接？**

```cpp
// 编译时：声明我需要一个输入端口
class GraspObject : public BT::SyncActionNode {
  static BT::PortsList providedPorts() {
    return { BT::InputPort<std::string>("target") };
  }
};

// 运行时 XML 决定它连到黑版的哪个 key
// <GraspObject target="{detected_obj}"/>    ← 连到 detected_obj
// <GraspObject target="{obj_to_grab}"/>     ← 连到 obj_to_grab
```

端口定义在 C++ 里（编译时确定类型安全），但连接到黑版的哪个 key 在 XML 里定（运行时灵活）。

---

## 这篇文档的知识结构图

```
Main Concepts
├── 1. Nodes vs Trees
│   ├── 叶子节点 = 乐高积木（C++ 写一次）
│   └── 树 = 积木模型（XML 随便搭）
├── 2. Run-time XML
│   ├── 编译一次
│   └── 换 XML 就是换行为
├── 3. tick() callbacks
│   ├── 函数指针注册：registerSimpleAction
│   └── 适合简单场景
├── 4. Inheritance
│   ├── ActionNodeBase / ConditionNode / DecoratorNode
│   └── 适合复杂场景
└── 5. Ports & Blackboard ★ 最重要
    ├── 黑版 = 键值存储（共享数据）
    ├── 端口 = 插孔（节点上的输入输出）
    ├── 端口类型在 C++ 定（编译时）
    └── 端口连接在 XML 定（运行时）
```

---

## 跟上一篇 BT_basics 的关系

| BT_basics | Main Concepts |
|---|---|
| 什么是 BT | 节点 vs 树的设计哲学 |
| 什么是 Tick | tick() 回调机制 |
| Sequence / Fallback | 如何自定义节点（函数指针 vs 继承） |
| SUCCESS / FAILURE / RUNNING | — |
| — | **Ports & Blackboard（新的核心概念）** |
| — | **XML 运行时加载（新的核心概念）** |

**一句话总结：**
> BT_basics 教你"行为树是什么"，Main Concepts 教你"BehaviorTree.CPP 这个库怎么设计、怎么用"。核心收获是两样——**端口/黑版传数据**、**XML 运行时换行为**。
