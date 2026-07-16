# 🧭 robot_localization：里程计平滑与传感器融合

> 学习日期：2026-07-15 | 整理人：小夏
>
> 参考：[Nav2 官方文档 - Smoothing Odometry using Robot Localization](https://docs.nav2.org/setup_guides/odom/setup_robot_localization.html)

---

## 目录

1. [这是什么？为什么要用？](#1-这是什么为什么要用)
2. [核心原理：一句话讲清楚 EKF](#2-核心原理一句话讲清楚-ekf)
3. [环境准备：安装](#3-环境准备安装)
4. [最关键的配置文件：ekf.yaml](#4-最关键的配置文件-ekfyaml)
5. [启动文件：把 EKF 加入你的 launch](#5-启动文件把-ekf-加入你的-launch)
6. [让 Nav2 使用平滑后的里程计](#6-让-nav2-使用平滑后的里程计)
7. [验证：看看它到底有没有用](#7-验证看看它到底有没有用)
8. [调参指南](#8-调参指南)
9. [常见问题](#9-常见问题)

---

## 1. 这是什么？为什么要用？

### 问题

机器人底盘通常有两个传感器：

| 传感器 | 提供的信息 | 问题 |
|--------|-----------|------|
| 🛞 **轮式里程计**（/wheel/odometry） | 轮子转了多少圈 → 推算走了多远 | 轮子打滑、地面不平 → 误差累积 |
| 🧲 **IMU**（/imu/data） | 加速度、角速度 → 推算姿态 | 长时间积分会漂移 |

**单独用哪一个都不靠谱**。轮子打滑时里程计说你走了 1 米，实际只走了 0.7 米。IMU 静止时会慢慢漂移，以为自己还在转。

### 解决方案

**把两个传感器的数据"融合"起来，取长补短**。

> 💡 **一句话**：robot_localization 就是一个"传感器混合器"，把轮子里程计和 IMU 的数据合在一起，输出一个更准确、更平滑的里程计。
>
> 它就像一个裁判：轮子说你走了 1m，IMU 说加速度是 0.7m/s²，裁判根据各自的"可信度"给出一个最优估计——大概走了 0.85m。

### 融合之后有什么好处？

```
融合前（只用轮子里程计）：
  路径：/\/\/\/\/\  （很多锯齿，不平滑）
  
融合后（EKF 输出）：
  路径：~~~~~~~~~~  （平滑、连续）
```

Nav2 用平滑的里程计做导航，路径跟踪会更准，机器人不会"抽搐"。

---

## 2. 核心原理：一句话讲清楚 EKF

### EKF 是什么？

**EKF = Extended Kalman Filter（扩展卡尔曼滤波器）**

Kalman Filter（卡尔曼滤波器）是一个数学算法，做一件事：

```
┌──────────┐     ┌──────────┐
│  预测     │ ──→ │  更新     │ ──→ 输出最优估计
│"按速度   │     │"传感器   │
│ 推算位置"│     │ 说我在哪" │
└──────────┘     └──────────┘
      ↑               ↑
   运动模型        传感器数据
   (轮子转速)     (IMU/激光)
```

1. **预测**：根据上一时刻机器人怎么动的，推算现在应该在哪儿
2. **更新**：用传感器实测值去校正这个推算
3. 不断循环，每秒跑 30 次（`frequency: 30.0`）

### 为什么叫"扩展"卡尔曼？

因为普通卡尔曼滤波只适用于**线性系统**，而机器人运动（比如转弯时）是**非线性**的。EKF 用一个数学技巧（泰勒展开在当前位置做线性近似）把非线性问题变成线性问题来解决。

> 不用深究数学原理，你只需要知道：EKF 是事实上的工业标准，几乎所有机器人都在用它。

### 数据流示意图

```
  /wheel/odometry ──┐
  (轮子里程计)       │
                    ├──→ [EKF 节点] ──→ /odometry/filtered （平滑输出）
  /imu/data ────────┘                  ──→ tf: odom → base_link
  (IMU 数据)
```

EKF 节点同时做两件事：
- 发布 `/odometry/filtered` 话题（平滑后的里程计数据）
- 发布 `odom → base_link` 的 TF 坐标变换

---

## 3. 环境准备：安装

```bash
# 一行命令搞定（把 $ROS_DISTRO 替换成你的 ROS2 版本名）
sudo apt install ros-$ROS_DISTRO-robot-localization

# 比如 Humble 版本：
sudo apt install ros-humble-robot-localization
```

---

## 4. 最关键的配置文件：ekf.yaml

> ⚠️ **这是整个设置中最重要的文件**。配错了，EKF 就不工作。

在你的机器人功能包里创建 `config/ekf.yaml`：

### 完整配置（带逐行解释）

```yaml
ekf_filter_node:                    # ← EKF 节点的名字（必须和 launch 文件中的 name 一致）
    ros__parameters:

        # ========== 基础设置 ==========

        frequency: 30.0             # 每秒运算多少次（Hz）。30 就够了，太高浪费 CPU
        sensor_timeout: 0.1         # 如果某个传感器 0.1 秒没发数据，就认为它"掉线了"
        two_d_mode: true            # ✅ 地面机器人一定要开！
                                    #    忽略 Z 轴（高度）的微小波动
                                    #    比如 IMU 检测到的地面小石子颠簸

        publish_acceleration: true  # 额外发布加速度数据（方便调试）
        publish_tf: true            # ✅ 必须开！EKF 会帮你发布 odom→base_link 的 TF

        # ========== 坐标系设置 ==========

        map_frame: map              # 地图坐标系（有全局地图时用）
        odom_frame: odom            # 里程计坐标系（EKF 发布的就是这个）
        base_link_frame: base_link  # 机器人中心坐标系
        world_frame: odom           # ✅ 关键！用 "odom" 作为世界参考系
                                    #    因为融合的是本地传感器（轮子+IMU），不是 GPS
        
        # ========== 传感器输入 0：轮式里程计 ==========

        odom0: /wheel/odometry      # 话题名（你的实际话题可能不同，改成你自己的）
        odom0_config:               # 15 个布尔值，告诉 EKF 这个传感器的哪些数据可信
            # 格式：[x, y, z,  roll, pitch, yaw,  vx, vy, vz,  vroll, vpitch, vyaw,  ax, ay, az]
            #       └─位置──┘  └───姿态───┘  └────速度────┘  └─────角速度────┘  └──加速度──┘
            [false, false, false,   # x, y, z 位置（轮子测不出绝对位置）
             false, false, false,   # roll, pitch, yaw 姿态（轮子测不出朝向）
             true,  true,  false,   # ✅ vx, vy 线速度（轮子能测这个！）  | vz 一般用不到
             false, false, true,    # vyaw 角速度（轮子能测转弯速度！）
             false, false, false]   # 加速度（轮子测不出）
        odom0_differential: false   # 不用微分模式

        # ========== 传感器输入 1：IMU ==========

        imu0: /imu/data             # 话题名（改成你自己的 IMU 话题）
        imu0_config:
            #       [x, y, z,  roll, pitch, yaw,  vx, vy, vz,  vroll, vpitch, vyaw,  ax, ay, az]
            [false, false, false,   # 位置（IMU 测不出位置）
             false, false, true,    # ✅ yaw 朝向（IMU 能测朝向！）
             false, false, false,   # 速度（IMU 一般不给速度）
             false, false, true,    # ✅ vyaw 角速度（IMU 的陀螺仪测这个很准！）
             true,  false, false]   # ✅ ax 线加速度（IMU 的加速度计测这个）
        imu0_differential: false
```

### config 数组速查卡片

```
     位置下标:  0=x   1=y   2=z
     姿态下标:  3=roll  4=pitch  5=yaw
     速度下标:  6=vx  7=vy  8=vz
    角速度下标:  9=vroll  10=vpitch  11=vyaw
    加速度下标: 12=ax  13=ay  14=az

记忆口诀：
  轮子 → 能测"走多快/转多快" → vx, vy, vyaw → 下标 6, 7, 11 填 true
  IMU  → 能测"朝向/转多快/加速度" → yaw, vyaw, ax → 下标 5, 11, 12 填 true
```

---

## 5. 启动文件：把 EKF 加入你的 launch

在你的 launch 文件中加入 EKF 节点：

### Python Launch 文件

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    # 获取你的功能包路径
    pkg_share = get_package_share_directory('你的功能包名')

    # EKF 节点
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',             # ← 可执行文件名
        name='ekf_filter_node',            # ← 节点名（必须和 yaml 中的名字一致！）
        output='screen',                   #   终端打印日志
        parameters=[
            os.path.join(pkg_share, 'config', 'ekf.yaml'),  # ← 配置文件路径
            {'use_sim_time': True}          #   仿真用 sim time，真机删掉这行
        ]
    )

    return LaunchDescription([
        # ... 你其他的节点（robot_state_publisher, 底盘驱动等）
        ekf_node,
        # ...
    ])
```

### 确认 CMakeLists.txt 安装了 config 目录

```cmake
# 确保 config 目录被安装到 share 目录
install(
  DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)
```

### 确认 package.xml 有依赖

```xml
<exec_depend>robot_localization</exec_depend>
```

---

## 6. 让 Nav2 使用平滑后的里程计

EKF 发布的话题是 `/odometry/filtered`，你需要告诉 Nav2 "用这个，不要用原始的"。

在你的 `nav2_params.yaml` 中：

```yaml
# 告诉 BT Navigator 用平滑后的里程计
bt_navigator:
  ros__parameters:
    odom_topic: /odometry/filtered

# 告诉速度平滑器用平滑后的里程计
velocity_smoother:
  ros__parameters:
    odom_topic: /odometry/filtered

# controller_server 也需要知道
controller_server:
  ros__parameters:
    odom_topic: /odometry/filtered
```

---

## 7. 验证：看看它到底有没有用

### 第一步：看话题是否正常

```bash
# 看看有没有 /odometry/filtered
ros2 topic list | grep odometry

# 应该能看到：
# /wheel/odometry        ← 原始轮子里程计
# /odometry/filtered     ← EKF 融合后的输出 ← 这是我们想要的！
```

### 第二步：检查 EKF 节点在不在运行

```bash
# 看节点列表
ros2 node list | grep ekf

# 查看节点详情（订阅了什么话题？发布了什么话题？）
ros2 node info /ekf_filter_node
```

应该看到：
```
Subscribers:
  /wheel/odometry           ← 订阅轮子数据 ✓
  /imu/data                 ← 订阅 IMU 数据 ✓
Publishers:
  /odometry/filtered        ← 发布融合结果 ✓
  /tf                       ← 发布 odom→base_link 的 TF ✓
```

### 第三步：看 TF 是否正确

```bash
# 检查 odom 到 base_link 的坐标变换
ros2 run tf2_ros tf2_echo odom base_link
```

如果正常运行，会持续打印以下内容（数值会变化，说明机器人在动）：
```
At time 123.456
- Translation: [0.123, 0.045, 0.000]
- Rotation: in Quaternion [0.000, 0.000, 0.012, 1.000]
```

### 第四步：对比原始数据和融合数据

```bash
# 开两个终端，同时看原始和融合后的数据
# 终端1：
ros2 topic echo /wheel/odometry

# 终端2：
ros2 topic echo /odometry/filtered
```

推动机器人（或用 `rqt_robot_steering` 遥控），观察：
- **原始 odom**：数据跳动大，有锯齿
- **融合后**：数据平滑，变化连续

### 第五步：可视化

```bash
# 打开 Rviz2
rviz2

# 在 RViz 中：
#   1. Fixed Frame 设为 "odom"
#   2. 添加 TF 显示（看 odom→base_link 有没有连起来）
#   3. 添加 Odometry 显示（选 /odometry/filtered 话题）
#   4. 推着机器人走，看路径是否平滑
```

---

## 8. 调参指南

### 核心调参参数

| 参数 | 默认值 | 作用 | 怎么调 |
|------|--------|------|--------|
| `frequency` | 30 | EKF 运算频率 | 太高耗 CPU，太低不平滑。30~50 之间就好 |
| `sensor_timeout` | 0.1 | 传感器超时时间 | 传感器不稳定时调大（如 0.2） |
| `two_d_mode` | true | 二维模式 | 地面机器人永远 true |

### 进阶：过程噪声协方差（Process Noise Covariance）

> ⚠️ 这部分比较难，新手先跳过。出问题了再回来看。

EKF 内部维护一个 15×15 的矩阵，叫**过程噪声协方差**。通俗理解：

```
过程噪声 = "我多信任运动模型的预测？"

值越小 → 更信任预测（路径更平滑，但响应慢）
值越大 → 更信任传感器（响应快，但可能抖动）
```

```yaml
# 默认值（一般不需要改）
process_noise_covariance: [0.05, 0.0, 0.0, ...]  # 15×15 对角矩阵
```

### 常见症状 vs 解决方案

| 症状 | 可能原因 | 解决办法 |
|------|----------|----------|
| 路径还是很抖 | 轮子 odom 的 noise 太大 | 减小 odom0 对应的 process_noise |
| 响应太慢 | EKF 太信预测，不信传感器 | 增大 process_noise 对应项 |
| 偶尔有突变 | IMU 或轮子有野值 | 检查传感器数据质量，增大 sensor_timeout |
| TF 没有发布 | `publish_tf` 没开 | `publish_tf: true` |
| EKF 节点起不来 | yaml 名字不匹配 | 检查 `ekf_filter_node` vs launch 中的 `name` |

---

## 9. 常见问题

### Q1: EKF 启动了但 `/odometry/filtered` 没有数据？

```
排查步骤：
1. 检查 /wheel/odometry 有没有数据：  ros2 topic echo /wheel/odometry
2. 检查 /imu/data 有没有数据：        ros2 topic echo /imu/data
3. 检查 EKF 节点状态：                ros2 node info /ekf_filter_node
4. 看 EKF 日志（看有没有报错）：      终端输出中找 [ekf_filter_node] 开头的行
```

**最常见的原因**：
- 话题名不对（yaml 里写的 `/wheel/odometry`，实际话题叫 `/odom`）
- IMU 还没启动
- `use_sim_time` 设错了（真机不要设 `true`）

### Q2: 和 robot_state_publisher 的关系是什么？

| 节点 | 发布什么 TF | 职责 |
|------|------------|------|
| `robot_state_publisher` | `base_link → 各个轮子/传感器` | 机器人**内部**的固定关系 |
| `ekf_filter_node` | `odom → base_link` | 机器人在世界中的**位置变化** |

两者不冲突，各管各的，必须**同时运行**。

### Q3: 我只有一个轮式里程计，没有 IMU，能用吗？

**能，但没必要。**

如果只有轮式里程计而没有其他传感器，EKF 就是"把数据原样过一遍"，没有融合效果。直接用原始 odom 就好。

EKF 的价值在于**融合多个传感器**。至少要有里程计 + IMU 才有意义。

### Q4: 能不能融合更多传感器？

可以！EKF 支持很多传感器输入：

```yaml
odom0: /wheel/odometry    # 第一个里程计
odom1: /visual_odometry   # 第二个里程计（如视觉里程计）
imu0:  /imu/data          # 第一个 IMU
imu1:  /imu/data_2        # 第二个 IMU（如果有）
pose0: /gps/filtered      # GPS 位置数据
twist0: /velodyne/vel     # 速度数据
```

每个传感器对应一组 `xxx_config: [15个布尔值]`，按需填写。

### Q5: UKF 和 EKF 有什么区别？我该用哪个？

| | EKF | UKF |
|------|-----|-----|
| 原理 | 数学近似（泰勒展开） | 采样近似（Sigma 点） |
| 精度 | 一般够用 | 在高度非线性场景下更好 |
| 速度 | 快 | 稍慢 |
| 推荐 | ✅ **99% 的场景都够了** | 无人机、极端机动等场景 |

**新手直接用 EKF，不要纠结。**

---

## 总结：设置检查清单

配置完成后，对照检查：

```
□ robot_localization 装好了吗？
  → sudo apt install ros-$ROS_DISTRO-robot-localization

□ ekf.yaml 配好了吗？
  → odom0_config 和 imu0_config 的下标填对了吗？
  → 话题名和实际发布的话题一致吗？

□ launch 文件加了 EKF 节点吗？
  → name 和 yaml 里的名字一致吗？

□ CMakeLists.txt 安装了 config 目录吗？
  → install(DIRECTORY config ...)

□ Nav2 参数指向 /odometry/filtered 了吗？
  → odom_topic: /odometry/filtered

□ 验证通过了吗？
  → ros2 topic echo /odometry/filtered  有数据吗？
  → ros2 run tf2_ros tf2_echo odom base_link  有输出吗？
```

---

> ✍️ **学习心得**：robot_localization 本质上就是一个"信号滤波器"，把不准确的传感器数据变成可信的、平滑的里程计。理解两个关键点就够了：
>
> 1. **config 数组**：15 个布尔值，告诉 EKF "这个传感器能测什么"——轮子能测速度（vx, vy, vyaw），IMU 能测朝向和角速度和加速度（yaw, vyaw, ax）。
> 2. **输出**：EKF 发布 `/odometry/filtered` 和 `odom→base_link` 的 TF，Nav2 用这个做导航。
>
> 大部分问题都出在**话题名不匹配**和**config 下标填错**，排查时先看这两处。
