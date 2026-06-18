# Sequences 逐段解释

> 来源：https://behaviortree.dev/docs/nodes-library/SequenceNode
> 说明：Nodes Library 最后一篇——Sequence（顺序节点）的完整参考。BT.CPP 提供了 **4 种** Sequence 变体。

---

## 一、核心概念

**原文：**
> Sequence 会依次 tick 所有子节点，只要它们返回 SUCCESS。如果任意一个返回 FAILURE，Sequence 立即中止。

**所有 Sequence 共享的规则：**

```
① tick 第一个子节点
② 如果子节点 SUCCESS → 继续下一个
③ 如果子节点 FAILURE → 停！返回 FAILURE
④ 如果最后一个也 SUCCESS → 返回 SUCCESS
```

---

## 二、四种 Sequence 变体

**原文的对比表：**

| 类型 | 子节点 FAILURE 时 | 子节点 RUNNING 时 | 子节点间让出执行权 |
|---|---|---|---|
| **Sequence** | 从头开始 | 下次 tick 继续同一个 | ❌ |
| **AsyncSequence** | 从头开始 | 下次 tick 继续同一个 | ✅ |
| **ReactiveSequence** | 从头开始 | **从头开始** | ❌ |
| **SequenceWithMemory** | **继续下一个** | 下次 tick 继续同一个 | ❌ |

**"从头开始"** = 下次 tick 从第一个子节点重新来  
**"继续下一个"** = 记住哪些已经成功过，不重跑  
**"继续同一个"** = RUNNING 状态的子节点保留，下次 tick 继续

---

## 三、Sequence（标准版）

**行为：**
- 一个 tick 内依次尝试所有子节点
- 一个成功立刻试下一个，不中断
- 遇到 FAILURE 就停
- 全部成功才返回 SUCCESS

```xml
<Sequence>
    <IsEnemyVisible/>      <!-- 条件 -->
    <AimAtEnemy/>          <!-- 瞄准 -->
    <FireWeapon/>          <!-- 开火 -->
    <ReloadWeapon/>        <!-- 换弹 -->
</Sequence>
```

---

## 四、AsyncSequence（异步版）⭐ 新内容

**原文核心：**
> AsyncSequence 跟 Sequence 逻辑一样，但**在每两个子节点之间会让出执行权**——返回 RUNNING 并发出唤醒信号。使 Sequence 在子节点之间**可以被中断**。

**典型场景：ReactiveSequence 包裹 AsyncSequence**

```xml
<ReactiveSequence>
    <IsEnemyVisible/>                   <!-- 条件，每次 tick 检查 -->
    <AsyncSequence>
        <AimAtEnemy/>                   <!-- 瞄准 → SUCCESS -->
        <FireWeapon/>                   <!-- 开火 → 还没轮到 -->
        <ReloadWeapon/>                 <!-- 换弹 → 还没轮到 -->
    </AsyncSequence>
</ReactiveSequence>
```

**执行流程：**

```
tick 1: IsEnemyVisible → SUCCESS ✅（敌人可见）
        AsyncSequence → AimAtEnemy → SUCCESS ✅
        → 返回 RUNNING 🔄（让出执行权）

tick 2: IsEnemyVisible → FAILURE ❌（敌人消失了！）
        → ReactiveSequence 检测到条件变化
        → AsyncSequence 被 halt！
        → FireWeapon 不会被执行！
```

**跟普通 Sequence 的区别：** 如果用普通 `Sequence`，`AimAtEnemy` 成功后会在同一 tick 内继续 `FireWeapon`，没有机会重新检查 `IsEnemyVisible`。

---

## 五、ReactiveSequence（响应式版）

**已在 Tutorial 04 详细讲过，这里只总结要点：**

- 第一个子节点每次 tick 都重新执行（通常是条件检查）
- 如果第一个子节点失败 → 直接 halt 后面的异步节点
- 适合：**需要实时监控条件**的场景

```xml
<ReactiveSequence>
    <IsBatteryOK/>         <!-- 条件，每次 tick 都检查 -->
    <ApproachEnemy/>       <!-- 异步 action，电量不足时被 halt -->
</ReactiveSequence>
```

---

## 六、SequenceWithMemory（记忆版）⭐ 新内容

**原文核心：**
> 当你**不想重新 tick 已经成功的子节点**时，用 SequenceWithMemory。

**典型场景：巡逻——必须依次经过 A → B → C 三个点，每个点只去一次**

```xml
<ReactiveSequence>
    <IsBatteryOK/>                    <!-- 条件，每次 tick 检查 -->
    <SequenceWithMemory>
        <GoTo location="A"/>          <!-- 到达 A 后不再重复 -->
        <GoTo location="B"/>          <!-- 到达 B 后不再重复 -->
        <GoTo location="C"/>          <!-- 到达 C 后不再重复 -->
    </SequenceWithMemory>
</ReactiveSequence>
```

**执行流程：**

```
tick 1: IsBatteryOK → SUCCESS
        SequenceWithMemory → GoTo(A) → 正在去 → RUNNING 🔄

tick n: IsBatteryOK → SUCCESS
        GoTo(A) → SUCCESS ✅（记住！不再重跑）
        GoTo(B) → 正在去 → RUNNING 🔄

tick m: IsBatteryOK → SUCCESS
        GoTo(A) → SUCCESS ✅（跳过）
        GoTo(B) → SUCCESS ✅（跳过）
        GoTo(C) → 正在去 → RUNNING 🔄
```

**关键区别：** 如果用普通 `Sequence`，GoTo(A) 每次 tick 都重新跑——永远到不了 B！

**用 SequenceWithMemory，已经成功的子节点会被记住**，下次 tick 直接跳过，继续执行还没成功的子节点。

---

## 七、四种 Sequence 对比总表

| 特性 | Sequence | AsyncSequence | ReactiveSequence | SequenceWithMemory |
|---|---|---|---|---|
| **FAILURE 时** | 从头开始 | 从头开始 | 从头开始 | **继续下一个** |
| **RUNNING 时** | 继续同一个 | 继续同一个 | **从头开始** | 继续同一个 |
| **让出执行权** | ❌ | ✅ | ❌ | ❌ |
| **记忆成功节点** | ❌ | ❌ | ❌ | ✅ |
| **适用场景** | 同步串联 | 需要条件重新评估 | 实时监控 | 每个任务只执行一次 |

---

**一句话总结：**
> Nodes Library 的 Sequence 家族收官篇。四种 Sequence 各有用处：标准 `Sequence` 最常用，`AsyncSequence` 给条件中途打断的机会，`ReactiveSequence` 实时监控条件，`SequenceWithMemory` 记住已成功的步骤不重跑。
