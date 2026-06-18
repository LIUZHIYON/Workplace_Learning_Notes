# Fallbacks (Controls) 逐段解释

> 来源：https://behaviortree.dev/docs/nodes-library/FallbackNode
> 说明：这篇是 Fallback（选择节点）系列的完整参考。BT.CPP 提供了 **3 种** Fallback 变体：Fallback、AsyncFallback、ReactiveFallback。

---

## 一、核心概念

**原文：**
> 这组节点在其他框架里叫"Selector"或"Priority"。它们的目的是尝试不同的策略，直到找到**一个可行的**。

**所有 Fallback 共享的规则：**

```
① tick 第一个子节点
② 如果子节点 FAILURE → 试下一个
③ 如果子节点 SUCCESS → 停！返回 SUCCESS
④ 如果最后一个也 FAILURE → 返回 FAILURE
```

**跟 Sequence 的对比：**

| 行为 | Fallback | Sequence |
|---|---|---|
| 遇到 SUCCESS | **立即返回 SUCCESS** | 继续下一个 |
| 遇到 FAILURE | 试下一个 | **立即返回 FAILURE** |
| 逻辑 | OR（一个成功就行） | AND（全部成功才行） |

---

## 二、三种 Fallback 变体

**原文的对比表：**

| 类型 | 子节点返回 RUNNING 时 | 子节点间是否让出执行权 |
|---|---|---|
| **Fallback** | 下次 tick 重新 tick 同一个子节点 | ❌ 不 |
| **AsyncFallback** | 下次 tick 重新 tick 同一个子节点 | ✅ **让出** |
| **ReactiveFallback** | **从头重新开始** | ❌ 不 |

---

## 三、Fallback（标准版）

**行为：**
- 在一个 tick 内，依次尝试所有子节点
- 一个失败立刻试下一个，**不中途返回**
- 遇到 SUCCESS 就停
- 全部失败才返回 FAILURE

```xml
<Fallback>
    <OpenDoor/>          <!-- 开门 -->
    <PickLock/>          <!-- 撬锁 -->
    <SmashDoor/>         <!-- 砸门 -->
</Fallback>
```

**执行流程（单次 tick 内）：**

```
tick 1:
  → OpenDoor → FAILURE ❌
  → PickLock → FAILURE ❌（继续下一个）
  → SmashDoor → SUCCESS ✅
  Fallback → SUCCESS ✅
```

---

## 四、AsyncFallback（异步版）

**原文核心：**
> AsyncFallback 跟 Fallback 逻辑一样，但**在每两个子节点之间会让出执行权**——返回 RUNNING 并发出唤醒信号。这使 Fallback 在子节点之间**可以被中断**。

**典型场景：ReactiveSequence 包裹 AsyncFallback**

```xml
<ReactiveSequence>
    <!-- 这个条件每次 tick 都会重新检查 -->
    <IsRobotHungry/>

    <!-- 尝试不同的找食物策略 -->
    <AsyncFallback>
        <FindFoodInBackpack/>
        <FindNearbyRestaurant/>
        <OrderFoodDelivery/>
    </AsyncFallback>
</ReactiveSequence>
```

**执行流程：**

```
tick 1: IsRobotHungry → SUCCESS（饿了）
        AsyncFallback → FindFoodInBackpack → FAILURE ❌（包里没吃的）
        → 返回 RUNNING 🔄（让出执行权，等下次 tick 再试）

tick 2: IsRobotHungry → FAILURE ❌（机器人突然不饿了！）
        → ReactiveSequence 检测到条件变化
        → AsyncFallback 被 halt！不会执行 FindNearbyRestaurant
        → ReactiveSequence 返回 FAILURE
```

**关键区别：** 如果用普通 `Fallback`，FindFoodInBackpack 失败后会在同一个 tick 里立刻执行 FindNearbyRestaurant，没有机会重新检查 IsRobotHungry。`AsyncFallback` 给了条件重新评估的机会。

---

## 五、ReactiveFallback（响应式版）

**原文核心：**
> 如果想在某个**异步子节点**正在 RUNNING 时，因为**前面的条件从 FAILURE 变成了 SUCCESS** 而中断它，就用 ReactiveFallback。

**典型场景：睡觉（最多睡 8 小时，但如果休息好了就提前醒）**

```
ReactiveFallback
├── AreYouRested？         ← 条件，每次 tick 都检查
└── Timeout(8hr)           ← 异步，睡眠中 → RUNNING
    └── Sleep
```

**执行流程：**

```
tick 1: AreYouRested → FAILURE（没休息好）
        → Timeout(8hr) → RUNNING 🔄（开始睡觉）

tick 2: AreYouRested → FAILURE（还在睡）
        → Sleep → RUNNING 🔄

tick 3: AreYouRested → SUCCESS ✅（休息好了！）
        → ReactiveFallback 立即返回 SUCCESS
        → Timeout 被 halt，Sleep 被中断
```

**用普通 Fallback 做不到这一点**——因为普通 Fallback 不会在子节点 RUNNING 时重新检查前面的条件。

---

## 六、三种 Fallback 对比总表

| 特性 | Fallback | AsyncFallback | ReactiveFallback |
|---|---|---|---|
| **子节点间让出执行权** | ❌ | ✅ | ❌ |
| **子节点 RUNNING 时下一 tick 的行为** | 继续同一个子节点 | 继续同一个子节点 | **从头开始** |
| **适合用在哪** | 同步节点串联尝试 | ReactiveSequence 内，需要条件重新评估 | 需要实时监控条件变化中断异步任务 |
| **条件变化时能中断吗** | ❌ | ✅（配合 ReactiveSequence） | ✅（自身就是响应式） |

---

**一句话总结：**
> 普通 `Fallback` = 一口气试完；`AsyncFallback` = 试一个停一下，让别人有机会插嘴；`ReactiveFallback` = 每次 tick 都从第一个条件开始重新判断。
