# Tutorial 07: Use multiple XML files 逐段解释

> 来源：https://behaviortree.dev/docs/tutorial-basics/tutorial_07_multiple_xml
> 说明：前面几篇所有树都写在一个 XML 文件里。这篇教你怎么**把不同子树拆分到多个 XML 文件**中管理。

---

## 一、问题背景

**原文大意：**
> 之前我们一直把整棵树和它的子树写在一个 XML 文件里。但随着子树越来越多，用**多个文件**更方便。

**我的解释：**

```
一个文件（混乱）              多个文件（整洁）
project/                      project/
├── all_trees.xml     ←        ├── main_tree.xml
                                ├── navigation.xml
                                ├── manipulation.xml
                                └── recovery.xml
```

每个文件里放**功能相关**的子树。

---

## 二、准备：两个子树文件

**原文给的例子——两个子树文件，各自只定义一棵树：**

**`subtree_A.xml`：**

```xml
<root>
    <BehaviorTree ID="SubTreeA">
        <SaySomething message="Executing Sub_A"/>
    </BehaviorTree>
</root>
```

**`subtree_B.xml`：**

```xml
<root>
    <BehaviorTree ID="SubTreeB">
        <SaySomething message="Executing Sub_B"/>
    </BehaviorTree>
</root>
```

**主树文件 `main_tree.xml`：**

```xml
<root>
    <BehaviorTree ID="MainTree">
        <Sequence>
            <SaySomething message="starting MainTree"/>
            <SubTree ID="SubTreeA"/>    <!-- 引用子树 A -->
            <SubTree ID="SubTreeB"/>    <!-- 引用子树 B -->
        </Sequence>
    </BehaviorTree>
</root>
```

---

## 三、方法 1：C++ 手动加载多个文件（推荐）

```cpp
int main()
{
  BT::BehaviorTreeFactory factory;
  factory.registerNodeType<DummyNodes::SaySomething>("SaySomething");

  // 逐个注册每个 XML 文件
  factory.registerBehaviorTreeFromFile("./main_tree.xml");
  factory.registerBehaviorTreeFromFile("./subtree_A.xml");
  factory.registerBehaviorTreeFromFile("./subtree_B.xml");

  // 创建主树
  std::cout << "----- MainTree tick ----" << std::endl;
  auto main_tree = factory.createTree("MainTree");
  main_tree.tickWhileRunning();

  // 也可以单独创建子树来测试
  std::cout << "----- SubA tick ----" << std::endl;
  auto subA_tree = factory.createTree("SubTreeA");
  subA_tree.tickWhileRunning();

  return 0;
}
```

**输出：**

```
Registered BehaviorTrees:
 - MainTree
 - SubTreeA
 - SubTreeB
----- MainTree tick ----
Robot says: starting MainTree
Robot says: Executing Sub_A
Robot says: Executing Sub_B
----- SubA tick ----
Robot says: Executing Sub_A
```

**关键点：**

```cpp
factory.registerBehaviorTreeFromFile("./xxx.xml");  // 注册文件到 factory
factory.createTree("ID");                           // 按 ID 创建树
```

**多个文件的更智能方法——自动扫描文件夹：**

```cpp
#include <filesystem>

std::string search_directory = "./";
for (auto const& entry : directory_iterator(search_directory))
{
    if (entry.path().extension() == ".xml")
    {
        factory.registerBehaviorTreeFromFile(entry.path().string());
    }
}
```

**推荐理由：**
- 显式控制加载顺序
- 可以单独创建子树来测试
- 文件依赖关系清晰

---

## 四、方法 2：XML 中用 `<include>` 指令

如果你不想在 C++ 里一个一个加载，可以在 XML 里用 `<include>`：

**改后的 `main_tree.xml`：**

```xml
<root BTCPP_format="4">
    <include path="./subtree_A.xml"/>    <!-- 引入子树文件 -->
    <include path="./subtree_B.xml"/>    <!-- 引入子树文件 -->
    <BehaviorTree ID="MainTree">
        <Sequence>
            <SaySomething message="starting MainTree"/>
            <SubTree ID="SubTreeA"/>
            <SubTree ID="SubTreeB"/>
        </Sequence>
    </BehaviorTree>
</root>
```

**C++ 端就只需要一行：**

```cpp
// 只需要加载主文件，include 的子树会自动加载
factory.createTreeFromFile("main_tree.xml");

// 等价于三行的效果：
//   factory.registerBehaviorTreeFromFile("./main_tree.xml");
//   factory.registerBehaviorTreeFromFile("./subtree_A.xml");
//   factory.registerBehaviorTreeFromFile("./subtree_B.xml");
```

**路径规则：** `<include path="...">` 的路径是**相对于主 XML 文件**的。

---

## 五、两种方法对比

| 维度 | 方法 1：C++ 手动加载 | 方法 2：XML `<include>` |
|---|---|---|
| 控制粒度 | 细——每步都看得见 | 粗——XML 里声明 |
| 可测试性 | ✅ 可以单独创建子树 | ❌ 必须加载整个文件 |
| 代码量 | 多一些（但清晰） | 少 |
| 报错定位 | 容易定位哪个文件出错 | 隐含在 include 里 |
| 推荐度 | **推荐**（原文说 recommended） | 适合简单场景 |

---

## 六、项目文件组织建议

```
project/
├── bt_main.cpp              ← 主程序
├── main_tree.xml             ← 主树
├── subtrees/                 ← 子树文件夹
│   ├── navigation.xml
│   │   <BehaviorTree ID="NavToPose">
│   │       ...
│   │   <BehaviorTree ID="NavThroughPoses">
│   │       ...
│   ├── manipulation.xml
│   │   <BehaviorTree ID="GraspObject">
│   │       ...
│   │   <BehaviorTree ID="PlaceObject">
│   │       ...
│   └── recovery.xml
│       <BehaviorTree ID="RecoverBattery">
│           ...
```

**C++ 端写法：**

```cpp
// 方法 1（推荐）：
factory.registerBehaviorTreeFromFile("main_tree.xml");
factory.registerBehaviorTreeFromFile("subtrees/navigation.xml");
factory.registerBehaviorTreeFromFile("subtrees/manipulation.xml");
factory.registerBehaviorTreeFromFile("subtrees/recovery.xml");
```

**也可以跟方法 2 结合——主树用 `<include>`，子树文件里再加 `<include>`：**

```
main_tree.xml
  <include path="subtrees/navigation.xml"/>
  <include path="subtrees/manipulation.xml"/>
  <include path="subtrees/recovery.xml"/>
```

这样 C++ 里就只需要：

```cpp
auto tree = factory.createTreeFromFile("main_tree.xml");
```

---

## 七、跟之前教程的关系

```
教程 04：ReactiveSequence —— 控制流
教程 05：SubTree —— 把一棵树嵌入另一棵树（同一文件）
教程 06：SubTree Port Remapping —— 子树间传数据
教程 07：Multiple XML files —— 把子树拆分到不同文件
                                        ↑
                              终于有了"真实项目"的目录结构
```

**一句话总结：**
> 用多个 XML 文件管理子树，C++ 端逐个 `registerBehaviorTreeFromFile()` 加载；或者在 XML 里用 `<include>` 自动加载。推荐方法 1，因为可以独立测试每棵子树。
