# Tutorial 15: Mocking and Nodes Replacement 逐段解释

> 来源：https://behaviortree.dev/docs/tutorial-advanced/tutorial_15_replace_rules
> 说明：这篇讲的是**测试替身（Mock）机制**——在不改 XML 的前提下，把行为树里的某些节点替换成"假的测试版"节点，方便做单元测试。

---

## 一、引入

**原文大意：**
> 做集成测试和单元测试时，经常需要把某个节点或某一类节点快速替换成"测试版"。
>
> 从 BT.CPP 4.1 开始，引入了**替换规则**机制，让你在**注册节点之后、创建树之前**设定替换规则。

**我的解释：**

```
生产环境：
  <SaySomething message="hello world"/>
  → 真的说出 "hello world"

测试环境：
  把 <SaySomething> 替换成 TestSaySomething
  → 只记录日志，不实际发音
```

**关键：XML 不用改！在 C++ 里设定规则就行了。**

---

## 二、替换规则的 API

```cpp
// 规则：把所有匹配 fullPath 为 "talk" 的节点，替换成 "TestSaySomething"
factory.addSubstitutionRule("talk", "TestSaySomething");
```

**第一个参数：通配符（wildcard）**  
匹配节点的 `fullPath`（参考 Tutorial 10 的路径规则）。

**第二个参数：替换成什么节点**  
可以是注册过的任意节点 ID。

---

## 三、TestNode——内置的 Mock 节点

**原文：**
> BT.CPP 提供了一个内置的 `TestNode`，你可以直接配置它：

**用 `TestNodeConfig` 配置 Mock 行为：**

```cpp
TestNodeConfig test_config;

// 设为异步模式，等 2000ms 才完成
test_config.async_delay = std::chrono::milliseconds(2000);

// 执行完成后，在黑板里写入一个值（模拟 OutputPort）
test_config.post_script = "msg ='message SUBSTITUTED'";

// 替换 "last_action" 节点为 TestNode，用它上面的配置
factory.addSubstitutionRule("last_action", test_config);
```

**`TestNodeConfig` 可配置项：**

| 配置项 | 类型 | 作用 |
|---|---|---|
| `async_delay` | `std::chrono::milliseconds` | 设为异步，延迟指定毫秒数后返回 |
| `post_script` | `std::string` | 执行完成后的脚本（模拟输出端口写入黑版） |

**注意：** 替换成 `TestNode` 时，`addSubstitutionRule` 的第二个参数是 `TestNodeConfig` 对象，不是字符串节点名。

---

## 四、完整示例流程

**C++ 注册 Mock 节点：**

```cpp
// 创建一个替换 SaySomething 的 Mock
factory.registerSimpleAction("TestSaySomething",
  [](BT::TreeNode& self) {
    auto msg = self.getInput<std::string>("message");
    std::cout << "TestSaySomething: " << msg.value() << std::endl;
    return BT::NodeStatus::SUCCESS;
  });

// 创建一个通用的 Mock Action
factory.registerSimpleAction("DummyAction",
  [](BT::TreeNode& self) {
    std::cout << "DummyAction substituting: " << self.name() << std::endl;
    return BT::NodeStatus::SUCCESS;
  });
```

**设定替换规则（在创建树之前）：**

```cpp
// 方式1：用通配符匹配路径
factory.addSubstitutionRule("mysub/action_*", "DummyAction");

// 方式2：精确匹配节点 name
factory.addSubstitutionRule("talk", "TestSaySomething");

// 方式3：用内置 TestNode + 配置
TestNodeConfig test_config;
test_config.async_delay = 2000ms;
test_config.post_script = "msg ='message SUBSTITUED'";
factory.addSubstitutionRule("last_action", test_config);
```

**创建树：**

```cpp
auto tree = factory.createTree("MainTree");
```

此时 `talk` 节点已经是 `TestSaySomething`，`mysub/` 子树内的 `action_*` 节点已经是 `DummyAction`，`last_action` 已经是 `TestNode`。

---

## 五、从 JSON 加载替换规则

```cpp
std::string json_text = R"(
[
  {
    "pattern": "mysub/action_*",
    "substitution": "DummyAction"
  },
  {
    "pattern": "talk",
    "substitution": "TestSaySomething"
  },
  {
    "pattern": "last_action",
    "node_type": "TestNode",
    "async_delay": 2000,
    "post_script": "msg='message SUBSTITUED'"
  }
])";

factory.loadSubstitutionRuleFromJSON(json_text);
```

**用 JSON 的好处：**
- 测试配置跟代码分离
- 同一个可执行文件，加载不同的 JSON 就得到不同的测试场景
- 非开发人员也可以配置

---

## 六、通配符匹配规则

`addSubstitutionRule` 的第一个参数是**通配符字符串**，匹配节点的 `fullPath`：

| 模式 | 匹配的节点 |
|---|---|
| `"talk"` | 精确匹配 name="talk" 的节点 |
| `"mysub/action_*"` | 子树 mysub 下所有 name 以 action_ 开头的节点 |
| `"*/action_subA"` | 任何子树下的 action_subA |
| `"*"` | 所有节点 |

**`fullPath` 复习（来自 Tutorial 10）：**

```
talk                          → 根树的 talk 节点
mysub/action_subA             → 子树 mysub 下的 action_subA
mysub/action_subB             → 子树 mysub 下的 action_subB
failing_action                → 根树的 failing_action
last_action                   → 根树的 last_action
```

---

## 七、总结

| 概念 | API | 说明 |
|---|---|---|
| 自定义替换 | `addSubstitutionRule(pattern, "NewNodeName")` | 用自己注册的 Mock 节点替换 |
| 内置 Mock | `addSubstitutionRule(pattern, TestNodeConfig)` | 用 `TestNode` 替换，可配置延迟和脚本 |
| JSON 加载 | `loadSubstitutionRuleFromJSON(json)` | 从 JSON 文件加载替换规则 |
| 模式匹配 | `"mysub/action_*"` | 通配符匹配 fullPath |

**一句话总结：**
> 替换规则让你在不改 XML 的前提下，在测试环境中把行为树的某些节点偷换成"替身"。`TestNode` 是内置的 mock 节点，配置简便。规则可以写在 C++ 里，也可以用 JSON 加载。
