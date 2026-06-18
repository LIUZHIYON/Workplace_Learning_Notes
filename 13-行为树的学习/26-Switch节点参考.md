# Switch Node 逐段解释

> 来源：https://behaviortree.dev/docs/nodes-library/SwitchNode
> 说明：这篇讲的是 **SwitchNode**——相当于 C++ 里的 `switch` 语句，根据变量的值选择执行哪个子节点。

---

## 一、核心概念

**原文大意：**
> SwitchNode 相当于一个 `switch` 语句：它根据黑版变量的值来选择执行哪个子节点。

**跟代码对比：**

```cpp
// C++ switch
switch (robot_state) {
  case IDLE:    HandleIdle(); break;
  case WORKING: HandleWorking(); break;
  case ERROR:   HandleError(); break;
  default:      HandleUnknown();
}
```

```xml
<!-- BT.CPP Switch -->
<Switch3 variable="{robot_state}"
         case_1="IDLE" case_2="WORKING" case_3="ERROR">
    <HandleIdle/>
    <HandleWorking/>
    <HandleError/>
    <HandleUnknownState/>    <!-- default -->
</Switch3>
```

---

## 二、变体：Switch2 ~ Switch6

**原文提供的变体：**

| 节点 | 支持的分支数 | 子节点总数 |
|---|---|---|
| `Switch2` | 2 个 case | 3 个（2 case + 1 default） |
| `Switch3` | 3 个 case | 4 个（3 case + 1 default） |
| `Switch4` | 4 个 case | 5 个 |
| `Switch5` | 5 个 case | 6 个 |
| `Switch6` | 6 个 case | 7 个 |

**规则：一个 `SwitchN` 节点必须有恰好 `N + 1` 个子节点——N 个 case 分支 + 1 个 default（最后一个子节点）。**

---

## 三、端口参数

| 端口 | 类型 | 说明 |
|---|---|---|
| `variable` | InputPort\<string\> | 黑版里的变量名（用于比较） |
| `case_1` | InputPort\<string\> | 第 1 个 case 的值 |
| `case_2` | InputPort\<string\> | 第 2 个 case 的值 |
| ... | ... | 直到 case_N |

**比较逻辑：**
> `variable` 的值依次跟每个 `case_N` 的字符串比较，匹配第一个就执行对应的子节点。如果没有匹配的，执行最后一个子节点（default）。

**支持的类型：** 字符串、整数、浮点数，以及通过 `ScriptingEnumsRegistry` 注册的枚举值。

---

## 四、XML 完整示例

```xml
<Switch3 variable="{robot_state}"
         case_1="IDLE"
         case_2="WORKING"
         case_3="ERROR">
    <!-- case_1: robot_state == "IDLE" -->
    <HandleIdle/>

    <!-- case_2: robot_state == "WORKING" -->
    <HandleWorking/>

    <!-- case_3: robot_state == "ERROR" -->
    <HandleError/>

    <!-- default: 没有匹配时 -->
    <HandleUnknownState/>
</Switch3>
```

**子节点跟 case 的对应关系：**

```
子节点位置    对应 case
  第 1 个   → case_1 = "IDLE"
  第 2 个   → case_2 = "WORKING"
  第 3 个   → case_3 = "ERROR"
  第 4 个   → default（最后一个）
```

---

## 五、响应式行为

**原文特意提到：**
> 如果匹配的子节点正在 RUNNING，而 `variable` 的值在后续的 tick 中发生了变化，**正在运行的子节点会被 halt**，然后执行新匹配的子节点。

**看例子：**

```
tick 1: robot_state = "IDLE"
  → 匹配 case_1 → 执行 HandleIdle → RUNNING 🔄

tick 2: robot_state = "WORKING"（变了！）
  → halt HandleIdle
  → 匹配 case_2 → 执行 HandleWorking → RUNNING 🔄

tick 3: robot_state = "ERROR"
  → halt HandleWorking
  → 匹配 case_3 → 执行 HandleError → SUCCESS ✅
```

**与 WhileDoElse 一样，Switch 是响应式的——条件变化时自动切换分支。**

---

## 六、跟 IfThenElse / WhileDoElse 的关系

| 节点 | 决策依据 | 分支数 | 响应式 |
|---|---|---|---|
| **IfThenElse** | 条件节点的 SUCCESS/FAILURE | 2~3 | ❌ |
| **WhileDoElse** | 条件节点（每次 tick 检查） | 2~3 | ✅ |
| **SwitchN** | 变量的值（数字/字符串/枚举） | 2~6 + default | ✅ |

**用 Switch 替代等效的 Fallback + Conditions：**

```xml
<!-- Fallback 方式——啰嗦 -->
<Fallback>
    <Sequence>
        <IsState value="IDLE"/>
        <HandleIdle/>
    </Sequence>
    <Sequence>
        <IsState value="WORKING"/>
        <HandleWorking/>
    </Sequence>
    <HandleUnknownState/>
</Fallback>

<!-- Switch 方式——简洁 -->
<Switch2 variable="{state}" case_1="IDLE" case_2="WORKING">
    <HandleIdle/>
    <HandleWorking/>
    <HandleUnknownState/>
</Switch2>
```

**官方说：** "同样的功能可以用多个 Sequence + Fallback + Condition 实现，但 Switch 更简洁易读。"

---

**一句话总结：**
> `SwitchN` 是行为树版本的 `switch-case`，根据黑版变量的值选择执行哪个 child，变量变化时自动 halt 当前分支切换到新分支。最多支持 Switch6（6 个 case + 1 个 default）。
