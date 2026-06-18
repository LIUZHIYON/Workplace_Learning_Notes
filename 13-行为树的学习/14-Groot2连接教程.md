# Tutorial 11: Connect to Groot2 逐段解释

> 来源：https://behaviortree.dev/docs/tutorial-basics/tutorial_11_groot2
> 说明：系列最后一篇——教你如何把你的行为树连接到 **Groot2 可视化工具**，实现编辑、监控、调试一体化。

---

## 一、Groot2 是什么

**原文大意：**
> Groot2 是 BT.CPP 的官方 IDE，用来**编辑、监控、交互**你的行为树。把它集成到你的 BT.CPP 程序里非常简单。

**我的解释：**

Groot2 三个核心功能：

| 功能 | 说明 |
|---|---|
| 🎨 **编辑（Edit）** | 拖拽画行为树，生成 XML |
| 📊 **监控（Monitor）** | 实时看到每个节点的 SUCCESS/FAILURE/RUNNING 状态 |
| 🐞 **调试（Debug）** | 设置断点、替换节点、注入故障 |

---

## 二、TreeNodesModel（节点模型）

**原文大意：**
> Groot 需要知道你的自定义节点长什么样，这叫 **TreeNode model**。包括：
> - 节点类型（Action / Condition / Decorator / Control）
> - 端口名字和类型（输入/输出）

**示例：**

```xml
<TreeNodesModel>
    <Action ID="SaySomething">
        <input_port name="message"/>
    </Action>
    <Action ID="ThinkWhatToSay">
        <output_port name="text"/>
    </Action>
</TreeNodesModel>
```

**但是——原文强调：你不需要手写这个 XML！**

```cpp
// 这一行自动生成所有注册过的节点模型
std::string xml_models = BT::writeTreeNodesModelXML(factory);
```

**把 xml_models 保存到文件，然后在 Groot2 里导入即可。**

---

## 三、Groot2 实时连接

**原文中的注意框：**
> ⚠️ 目前只有 **Groot2 PRO 版本**支持实时可视化。

**连接代码——只有一行：**

```cpp
BT::Groot2Publisher publisher(tree);
```

**Groot2Publisher 提供的功能：**

| 功能 | 说明 |
|---|---|
| 发送树结构 | 把整棵树的结构发给 Groot2 |
| 实时状态更新 | 每个节点的 RUNNING/SUCCESS/FAILURE 实时刷新 |
| 黑版数据 | 显示 blackboard 里的值（int/float/string 自动支持） |
| 调试功能 | Groot2 可以设置断点、替换节点、注入故障 |

---

## 四、完整示例（C++ 代码）

```cpp
int main()
{
  BT::BehaviorTreeFactory factory;

  // 注册自定义节点
  CrossDoor cross_door;
  cross_door.registerNodes(factory);

  // 1. 生成节点模型（给 Groot2 用）
  std::string xml_models = BT::writeTreeNodesModelXML(factory);

  // 2. 注册 XML 并创建树
  factory.registerBehaviorTreeFromText(xml_text);
  auto tree = factory.createTree("MainTree");

  // 3. 连接 Groot2（核心！）
  BT::Groot2Publisher publisher(tree);

  // 4. 无限循环运行
  while (true) {
    std::cout << "Start" << std::endl;
    cross_door.reset();
    tree.tickWhileRunning();
    std::this_thread::sleep_for(std::chrono::milliseconds(3000));
  }

  return 0;
}
```

---

## 五、让 Groot2 显示自定义类型的黑版数据

默认支持：int、float、double、string。

自定义类型（如 `Position2D`）需要加 JSON 转换器。

### 方法 1：用 `BT_JSON_CONVERTER` 宏（推荐）

**定义结构体：**

```cpp
struct Position2D {
  double x;
  double y;
};
```

**在文件作用域定义转换器（任何函数外面）：**

```cpp
#include "behaviortree_cpp/json_export.h"

BT_JSON_CONVERTER(Position2D, pos) {
  add_field("x", &pos.x);
  add_field("y", &pos.y);
}
```

**支持嵌套类型：**

```cpp
struct Waypoint {
  std::string name;
  Position2D position;
  double speed = 1.0;
};

BT_JSON_CONVERTER(Waypoint, wp) {
  add_field("name", &wp.name);
  add_field("position", &wp.position);  // 嵌套！
  add_field("speed", &wp.speed);
}
```

**在 main 里注册：**

```cpp
BT::RegisterJsonDefinition<Position2D>();
BT::RegisterJsonDefinition<Waypoint>();
```

### 方法 2：手动写转换函数

```cpp
void to_json(nlohmann::json& j, const Position2D& pos) {
  j = nlohmann::json{{"x", pos.x}, {"y", pos.y}};
}
// 然后手动注册...
```

---

## 六、Groot2 使用流程总结

```
你的开发机：
  1. 写 C++ 节点 + XML 行为树
  2. 在 main 里写：
     auto models = BT::writeTreeNodesModelXML(factory);  // 生成模型
     BT::Groot2Publisher publisher(tree);                // 启动发布
  3. 启动程序

Groot2：
  4. 打开 Groot2
  5. Import Models → 导入生成的模型 XML
  6. 连接 → 实时看到树结构 + 节点状态 + 黑版数据
  7. 可以设置断点、注入故障调试
```

---

## 七、跟整个系列的关系

```
Tutorial 01~09：学会写行为树
Tutorial 10：   学会用 Observer 做单元测试
Tutorial 11：   学会用 Groot2 做可视化编辑和调试

至此，你拿到了行为树开发的完整工具链：
  编写（C++ + XML）→ 验证（单元测试）→ 可视化（Groot2）
```

---

**一句话总结：**
> 两行代码搞定 Groot2 集成：`BT::writeTreeNodesModelXML(factory)` 生成节点模型供导入，`BT::Groot2Publisher publisher(tree)` 实现实时连接。然后就能在 Groot2 里看到整棵树的运行状态，甚至打断点调试。
