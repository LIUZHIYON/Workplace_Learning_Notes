# The XML schema 逐段解释

> 来源：https://behaviortree.dev/docs/learn-the-basics/xml_format
> 说明：这篇讲的是 BehaviorTree.CPP 的 XML 语法规则——怎么用 XML 写一棵行为树。

---

## 一、最基本的 XML 结构

**原文给的示例：**

```xml
<root BTCPP_format="4">
    <BehaviorTree ID="MainTree">
        <Sequence name="root_sequence">
            <SaySomething   name="action_hello" message="Hello"/>
            <OpenGripper    name="open_gripper"/>
            <ApproachObject name="approach_object"/>
            <CloseGripper   name="close_gripper"/>
        </Sequence>
    </BehaviorTree>
</root>
```

**我的解释：**

这是最基础的一棵行为树，翻译成人话：

```
根节点 root (BTCPP_format 版本 4)
└── 行为树 (ID = MainTree)
    └── Sequence (挨个执行)
        ├── SaySomething    → 说 "Hello"
        ├── OpenGripper     → 打开夹爪
        ├── ApproachObject  → 靠近物体
        └── CloseGripper    → 关闭夹爪
```

---

## 二、XML 的 4 条硬性规则

**原文列举了 4 点：**

1. **`<root>`** 是树的第一个标签，里面包含 **1 个或多个** `<BehaviorTree>` 标签
2. **`<BehaviorTree>`** 必须有属性 **`ID`**
3. **`<root>`** 必须有属性 **`BTCPP_format`**
4. 每个节点用一个标签表示，其中：
   - **标签名** = 注册到 factory 时的 ID（比如 SaySomething、OpenGripper）
   - **`name` 属性** = 实例名，**可选**
   - **端口（Ports）** 用属性配置，比如 `message="Hello"`

**关于子节点数量：**

| 节点类型 | 子节点数量 |
|---|---|
| ControlNode（Sequence / Fallback 等） | 1 ~ N 个子节点 |
| DecoratorNode（装饰器） | **只有 1 个**子节点 |
| SubTree（子树） | **只有 1 个**子节点 |
| ActionNode / ConditionNode（叶子节点） | **0 个**子节点（它们就是树叶） |

**我的解释：**

```
ControlNode 可以有多个孩子：
  <Sequence>
    <Child1/>
    <Child2/>
    <Child3/>
  </Sequence>

DecoratorNode 只能有一个孩子：
  <Inverter>
    <SaySomething message="hello"/>   ← 只有一个
  </Inverter>

ActionNode 不能有孩子：
  <SaySomething message="hello"/>     ← 自闭合标签
```

---

## 三、端口映射：用 `{key_name}` 连接黑版

**原文：**
> 输入/输出端口可以用黑版里的 key 来重新映射（remap），语法是 `{key_name}`。

**示例：**

```xml
<Sequence>
  <SaySomething message="Hello"/>                <!-- 固定字符串 -->
  <SaySomething message="{my_message}"/>          <!-- 从黑版读取 -->
</Sequence>
```

**我的解释：**

| 写法 | 含义 |
|---|---|
| `message="Hello"` | 传一个**固定字符串** "Hello" |
| `message="{my_message}"` | 从黑版里读 key 为 `my_message` 的值 |

```
黑版（Blackboard）
┌────────────────────┐
│ "my_message" = ... │ ← 别的节点写入的值
└────────────────────┘
        ↑
<SaySomething message="{my_message}"/>
  从黑版读取，而不是硬编码
```

---

## 四、Compact vs Explicit（简洁写法 vs 显式写法）

**原文对比：**

两种写法都合法：

```xml
<!-- 简洁写法（compact）：标签名 = 节点 ID -->
<SaySomething name="action_hello" message="Hello World"/>

<!-- 显式写法（explicit）：用 <Action ID="..."> 指明类型 -->
<Action ID="SaySomething" name="action_hello" message="Hello World"/>
```

**简洁写法版完整树：**

```xml
<root BTCPP_format="4">
  <BehaviorTree ID="MainTree">
    <Sequence name="root_sequence">
      <SaySomething   name="action_hello" message="Hello"/>
      <OpenGripper    name="open_gripper"/>
      <ApproachObject name="approach_object"/>
      <CloseGripper   name="close_gripper"/>
    </Sequence>
  </BehaviorTree>
</root>
```

**显式写法版完整树：**

```xml
<root BTCPP_format="4">
  <BehaviorTree ID="MainTree">
    <Sequence name="root_sequence">
      <Action ID="SaySomething"   name="action_hello" message="Hello"/>
      <Action ID="OpenGripper"    name="open_gripper"/>
      <Action ID="ApproachObject" name="approach_object"/>
      <Action ID="CloseGripper"   name="close_gripper"/>
    </Sequence>
  </BehaviorTree>
</root>
```

**我的解释：**

| 写法 | 标签名是啥 | 优点 | 缺点 |
|---|---|---|---|
| **Compact** | 直接用节点 ID（如 `<SaySomething>`、`<OpenGripper>`） | 简洁好写 | Groot 不认识，没节点类型信息 |
| **Explicit** | 统一用 `<Action>`、`<Condition>`、`<Control>`、`<Decorator>`，ID 用属性 | Groot 能识别 | 啰嗦 |

**什么时候用哪种？**

- 不用 Groot 纯手写 → **Compact** 就行，省事
- 要用 Groot 可视化编辑 → **Explicit** 或者加 `<TreeNodeModel>`

---

## 五、TreeNodeModel：让 Groot 能识别 Compact 写法

**原文说：**
> 如果你喜欢 Compact 写法但又想用 Groot，可以在 XML 底部加 `<TreeNodeModel>` 段来补充节点信息。

```xml
<root BTCPP_format="4">
  <BehaviorTree ID="MainTree">
    <Sequence name="root_sequence">
      <SaySomething   name="action_hello" message="Hello"/>
      <OpenGripper    name="open_gripper"/>
      <ApproachObject name="approach_object"/>
      <CloseGripper   name="close_gripper"/>
    </Sequence>
  </BehaviorTree>

  <!-- 辅助段：给 Groot 看的节点定义 -->
  <TreeNodeModel>
    <Action ID="SaySomething">
      <input_port name="message" type="std::string"/>
    </Action>
    <Action ID="OpenGripper"/>
    <Action ID="ApproachObject"/>
    <Action ID="CloseGripper"/>
  </TreeNodeModel>
</root>
```

**我的解释：**

```
文件结构分成两段：
  ┌─────────────────────────────────────┐
  │ 第1段：BehaviorTree（执行引擎用的）  │  ← 实际树逻辑
  │ <BehaviorTree ID="MainTree">...     │
  │                                     │
  │ 第2段：TreeNodeModel（Groot用的）    │  ← 给 GUI 工具看的
  │ <TreeNodeModel>...                  │
  └─────────────────────────────────────┘
```

第 1 段是**执行引擎**读的，告诉你树长什么样。
第 2 段是 **Groot 编辑器**读的，告诉它每个节点有什么端口。

---

## 六、Subtrees（子树复用）

**原文示例：**

```xml
<root BTCPP_format="4">

  <!-- 主树 -->
  <BehaviorTree ID="MainTree">
    <Sequence>
      <Action ID="SaySomething"  message="Hello World"/>
      <SubTree ID="GraspObject"/>                    <!-- ← 引用子树 -->
    </Sequence>
  </BehaviorTree>

  <!-- 子树定义 -->
  <BehaviorTree ID="GraspObject">
    <Sequence>
      <Action ID="OpenGripper"/>
      <Action ID="ApproachObject"/>
      <Action ID="CloseGripper"/>
    </Sequence>
  </BehaviorTree>

</root>
```

**我的解释：**

子树 = **把你重复用的行为片段抽出来，在别的地方引用它**。

```
想像一下，你有好几个场景都要"抓取物体"：

  场景A：  先说话 → 再抓取
  场景B：  先检查 → 再抓取 → 再检查
  场景C：  直接抓取

如果不抽子树，每个场景都要复制粘贴 OpenGripper / ApproachObject / CloseGripper
三个节点。抽成子树后：
```

```xml
<!-- 只写一次抓取流程 -->
<BehaviorTree ID="GraspObject">
  <Sequence>
    <OpenGripper/>
    <ApproachObject/>
    <CloseGripper/>
  </Sequence>
</BehaviorTree>

<!-- 三个场景都引用同一个子树 -->
场景A：<Sequence> <SaySomething/> <SubTree ID="GraspObject"/> </Sequence>
场景B：<Sequence> <Check/> <SubTree ID="GraspObject"/> <Check/> </Sequence>
场景C：<SubTree ID="GraspObject"/>
```

**画成树：**

```
MainTree                         ← 主树，<= 10 行
└── Sequence
    ├── SaySomething
    └── SubTree ID="GraspObject" ← 引用子树
                  │
        ┌─────────┘
        ▼
GraspObject                      ← 子树定义，单独维护
└── Sequence
    ├── OpenGripper
    ├── ApproachObject
    └── CloseGripper
```

**子树的端口映射（进阶）：**

子树的 `<SubTree>` 标签也可以有端口映射：

```xml
<SubTree ID="GraspObject" target="{detected_obj}" />
```

子树内部用 `{target}` 从黑版读取数据。

---

## 七、Include 外部文件

**原文：**
> 版本 2.4 开始可以用 `#include` 类似的机制引用外部文件。

```xml
<root BTCPP_format="4">
  <include path="grasp_subtree.xml"/>
  <BehaviorTree ID="MainTree">
    ...
  </BehaviorTree>
</root>
```

**我的解释：**

跟 C++ 的 `#include` 一个道理——把子树定义放到单独文件里，主 XML 干净整洁。

```
project/
├── main_tree.xml           ← 主树，只引用
└── trees/
    ├── grasp_subtree.xml   ← 抓取流程
    └── recovery.xml        ← 恢复流程
```

---

## 这篇文档的知识点结构

```
XML schema
├── 基本结构
│   ├── <root BTCPP_format="4">
│   ├── <BehaviorTree ID="...">
│   └── 各种节点标签
├── 4 条硬性规则
│   ├── root 必须含 BTCPP_format
│   ├── BehaviorTree 必须含 ID
│   ├── 各类型节点子节点数量限制
│   └── 端口用属性配置
├── 端口映射 {key_name}
│   ├── 固定值: message="Hello"
│   └── 黑版引用: message="{my_message}"
├── Compact vs Explicit
│   ├── Compact: <SaySomething/> 简洁但 Groot 不识别
│   ├── Explicit: <Action ID="SaySomething"/> Groot 能识别
│   └── TreeNodeModel: 在底部补充节点信息
├── Subtrees（子树）
│   ├── <SubTree ID="GraspObject"/>
│   ├── 复用行为
│   └── 端口映射
└── Include 外部文件
    └── <include path="file.xml"/>
```

---

## 三篇基础概念的关系

| 文档 | 学什么 |
|---|---|
| BT_basics | 什么是行为树、Sequence/Fallback、3 种返回值 |
| Main Concepts | 设计思想 - 乐高积木、tick 回调、端口/黑版 |
| **XML schema（这篇）** | **怎么写 XML —— 具体的语法规则** |

**一句话总结：**
> BT_basics 和 Main Concepts 教你"是什么、为什么"，这篇 XML schema 教你"怎么写在文件里"。
