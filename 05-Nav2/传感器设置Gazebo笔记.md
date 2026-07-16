# 🔬 Nav2 传感器设置（Gazebo Classic）

> 学习日期：2026-07-15 | 整理人：小夏
>
> 参考：[Nav2 官方文档 - Setting Up Sensors (Gazebo Classic)](https://docs.nav2.org/setup_guides/sensors/setup_sensors_gz_classic.html)

---

## 目录

1. [这是什么？为什么要看这个？](#1-这是什么为什么要看这个)
2. [传感器入门：机器人有哪些"眼睛"？](#2-传感器入门机器人有哪些眼睛)
3. [第一步：在 URDF 中添加激光雷达 LIDAR](#3-第一步在-urdf-中添加激光雷达-lidar)
4. [第二步：在 URDF 中添加深度相机](#4-第二步在-urdf-中添加深度相机)
5. [第三步：启动文件配置](#5-第三步启动文件配置)
6. [第四步：CMakeLists.txt 和 package.xml](#6-第四步cmakeliststxt-和-packagexml)
7. [第五步：在 RViz 中验证传感器](#7-第五步在-rviz-中验证传感器)
8. [第六步：把传感器传给 Nav2 代价地图](#8-第六步把传感器传给-nav2-代价地图)
9. [完整流程图](#9-完整流程图)
10. [常见问题](#10-常见问题)

---

## 1. 这是什么？为什么要看这个？

> 💡 **一句话**：这篇教你如何在 Gazebo 仿真中给机器人装上"眼睛"——激光雷达（LIDAR）和深度相机（Depth Camera），让机器人能"看见"周围的环境，从而实现避障。

在真实机器人上，你需要连接真实的传感器硬件。但在 Gazebo 仿真中，我们通过**插件（Plugin）**来模拟传感器，效果和真的一样，而且不花钱。

### 你将学会

```
┌─────────────────────────────────────────┐
│ ✅ 在 URDF 中定义传感器（LIDAR / 相机）│
│ ✅ 配置 Gazebo 传感器插件              │
│ ✅ 验证传感器数据是否正常              │
│ ✅ 把传感器数据喂给 Nav2 做导航        │
└─────────────────────────────────────────┘
```

---

## 2. 传感器入门：机器人有哪些"眼睛"？

Nav2 支持四种传感器数据类型：

| 类型 | ROS 消息格式 | 来源 | 长什么样 |
|------|-------------|------|----------|
| 🔴 **LaserScan** | `sensor_msgs/LaserScan` | 2D 激光雷达、单线 LIDAR | 平面的一圈点（像一把扇子） |
| 🟡 **PointCloud2** | `sensor_msgs/PointCloud2` | 3D LIDAR、深度相机、RGB-D 相机 | 空间中一堆 3D 点（像一团雾） |
| 🟢 **Range** | `sensor_msgs/Range` | 超声波、红外传感器 | 单个距离值（像一根棒子戳出去） |
| 🔵 **Image** | `sensor_msgs/Image` | RGB 相机、深度相机 | 普通图片（640×480 等） |

### 本篇要装的两个传感器

```
1. 激光雷达 LIDAR（2D）
   → 插件：libgazebo_ros_ray_sensor.so
   → 发布：/scan（sensor_msgs/LaserScan）
   → 用途：SLAM建图、AMCL定位、避障
   
2. 深度相机 Depth Camera（3D）
   → 插件：libgazebo_ros_camera.so
   → 发布：/depth_camera/image_raw（sensor_msgs/Image）
             /depth_camera/points（sensor_msgs/PointCloud2）
   → 用途：3D避障、物体识别
```

---

## 3. 第一步：在 URDF 中添加激光雷达（LIDAR）

### 3.1 在脑海里画个图

URDF 就是机器人的"骨架描述文件"。你要告诉 Gazebo：

1. 传感器长什么样？（link：形状、颜色、重量）
2. 传感器装在哪？（joint：和谁连在一起，偏移多少）
3. 传感器怎么做数据？（plugin：Gazebo 的仿真插件）

```
  [base_link] ──(lidar_joint)── [lidar_link]  ← 🔴 激光雷达装在底座上方
       ↑ 机器人的根              ↑ 传感器的 link
```

### 3.2 完整的 URDF 代码（放到你的 robot.urdf.xacro 里）

```xml
<!-- ============================================ -->
<!--  激光雷达 LIDAR                              -->
<!-- ============================================ -->

<!-- 1. 定义传感器的"身体"：link -->
<link name="lidar_link">
  <inertial>
    <!-- 重心在传感器正中心 -->
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="0.125"/>
    <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
  </inertial>

  <collision>
    <!-- 碰撞箱：一个扁圆柱体（半径 5cm，高 5.5cm）-->
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.0508" length="0.055"/>
    </geometry>
  </collision>

  <visual>
    <!-- 外观：一个蓝色的小圆柱体 -->
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <cylinder radius="0.0508" length="0.055"/>
    </geometry>
    <material name="blue"/>
  </visual>
</link>

<!-- 2. 把传感器"固定"在机器人身上：joint -->
<joint name="lidar_joint" type="fixed">
  <parent link="base_link"/>        <!-- 装在 base_link 上面 -->
  <child link="lidar_link"/>
  <origin xyz="0 0 0.12" rpy="0 0 0"/>  <!-- 比 base_link 高 12cm -->
</joint>

<!-- 3. 配置仿真插件：告诉 Gazebo 怎么模拟这个传感器 -->
<gazebo reference="lidar_link">
  <sensor name="lidar" type="ray">    <!-- type="ray" 表示光线传感器 -->

    <!-- 基础设置 -->
    <always_on>true</always_on>       <!-- 一直开着 -->
    <visualize>true</visualize>        <!-- 在 Gazebo 里可视化射线 -->
    <update_rate>5</update_rate>      <!-- 每秒扫描 5 次 -->

    <!-- 扫描配置 -->
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>      <!-- 一圈扫 360 个点（每 1° 一个点） -->
          <resolution>1.0</resolution> <!-- 角分辨率 1° -->
          <min_angle>0.0</min_angle>   <!-- 从 0° 开始 -->
          <max_angle>6.28</max_angle>  <!-- 到 360°（6.28弧度量）= 扫一整圈 -->
        </horizontal>
      </scan>

      <range>
        <min>0.12</min>               <!-- 最近能测 12cm（太近测不准） -->
        <max>3.5</max>                <!-- 最远能测 3.5m -->
        <resolution>0.015</resolution> <!-- 距离分辨率 1.5cm -->
      </range>

      <!-- 模拟噪声：真实传感器不是 100% 精准的 -->
      <noise>
        <type>gaussian</type>          <!-- 高斯噪声 -->
        <mean>0.0</mean>               <!-- 平均误差为 0 -->
        <stddev>0.01</stddev>          <!-- 标准差 0.01（大部分测量误差在 ±1cm 以内） -->
      </noise>
    </ray>

    <!-- Gazebo ROS 插件：把仿真数据转成 ROS 消息 -->
    <plugin name="scan" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <!-- 重映射：插件默认输出 ~/out，我们改成 /scan -->
        <remapping>~/out:=scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>  <!-- 输出格式 -->
      <frame_name>lidar_link</frame_name>               <!-- 数据绑定的坐标系 -->
    </plugin>
  </sensor>
</gazebo>
```

### 3.3 LIDAR 参数速查

| 参数 | 含义 | 建议值 |
|------|------|--------|
| `samples` | 一圈扫多少个点 | 360（每个点 1°） |
| `min_angle` | 起始角度 | 0 |
| `max_angle` | 终止角度 | 6.28（360°） |
| `min`（range）| 最近探测距离 | 0.12m |
| `max`（range）| 最远探测距离 | 3.5m |
| `update_rate` | 扫描频率 | 5~10 Hz |
| `stddev`（noise）| 噪声标准差 | 0.01（越小越准） |

---

## 4. 第二步：在 URDF 中添加深度相机

### 4.1 坐标关系

深度相机比 LIDAR 稍微复杂一点，因为它有两个坐标 frame：

```
[base_link] ──(camera_joint)── [camera_link] ──(camera_depth_joint)── [camera_depth_frame]
   ↑ 机器人底座                  ↑ 相机机身（安装点）                ↑ 深度数据的坐标系
                                 偏移量：往前21.5cm，高5cm              需要旋转让 Z 轴朝前
```

> ⚠️ **重要**：ROS 的深度相机默认坐标系是 Z 轴朝前，但 Gazebo 的相机坐标系是 X 轴朝前。所以需要旋转 `${-pi/2} 0 ${-pi/2}`（绕 X 轴转 -90°，绕 Z 轴转 -90°）来对齐。

### 4.2 完整的 URDF 代码

```xml
<!-- ============================================ -->
<!--  深度相机 Depth Camera                       -->
<!-- ============================================ -->

<!-- 1. 相机机身 link -->
<link name="camera_link">
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.015 0.130 0.022"/>   <!-- 一个扁长的盒子形状 -->
    </geometry>
    <material name="black"/>
  </visual>

  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry>
      <box size="0.015 0.130 0.022"/>
    </geometry>
  </collision>

  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <mass value="0.035"/>               <!-- 35g，很轻 -->
    <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.001"/>
  </inertial>
</link>

<!-- 2. 相机机身 → base_link -->
<joint name="camera_joint" type="fixed">
  <parent link="base_link"/>
  <child link="camera_link"/>
  <!-- 装在机器人前方靠上：前21.5cm，高5cm -->
  <origin xyz="0.215 0 0.05" rpy="0 0 0"/>
</joint>

<!-- 3. 深度坐标系 frame（只是一个空 link，没有体积） -->
<link name="camera_depth_frame"/>

<!-- 4. 深度坐标系 → 相机机身（旋转对齐） -->
<joint name="camera_depth_joint" type="fixed">
  <!-- 🔑 关键旋转！把 Gazebo 的 X轴朝前 转成 ROS 的 Z轴朝前 -->
  <origin xyz="0 0 0" rpy="${-pi/2} 0 ${-pi/2}"/>
  <parent link="camera_link"/>
  <child link="camera_depth_frame"/>
</joint>

<!-- 5. Gazebo 深度相机插件 -->
<gazebo reference="camera_link">
  <sensor name="depth_camera" type="depth">   <!-- type="depth" = 深度传感器 -->

    <visualize>true</visualize>
    <update_rate>30.0</update_rate>            <!-- 每秒 30 帧 -->

    <!-- 相机内部参数 -->
    <camera name="camera">
      <horizontal_fov>1.047198</horizontal_fov>  <!-- 水平视场角 60°（弧度量） -->
      <image>
        <width>640</width>                       <!-- 图像宽 640 像素 -->
        <height>480</height>                     <!-- 图像高 480 像素 -->
        <format>R8G8B8</format>                  <!-- RGB 8位彩色 -->
      </image>
      <clip>
        <near>0.05</near>                        <!-- 最近 5cm 以内看不到 -->
        <far>3</far>                             <!-- 最远 3m 以外看不到 -->
      </clip>
    </camera>

    <!-- Gazebo ROS 深度相机插件 -->
    <plugin name="depth_camera_controller" filename="libgazebo_ros_camera.so">
      <baseline>0.2</baseline>                   <!-- 基线距离（立体视觉用） -->

      <alwaysOn>true</alwaysOn>
      <updateRate>0.0</updateRate>               <!-- 0 表示跟随传感器 update_rate -->

      <frame_name>camera_depth_frame</frame_name>  <!-- 数据绑定坐标系 -->

      <!-- 点云裁剪范围（只保留这个距离范围内的点云） -->
      <pointCloudCutoff>0.5</pointCloudCutoff>       <!-- 0.5m 以内的点不要（太近无意义） -->
      <pointCloudCutoffMax>3.0</pointCloudCutoffMax> <!-- 3m 以外的点不要（太远不准） -->

      <!-- 畸变参数（仿真中都设为 0，表示理想镜头无畸变） -->
      <distortionK1>0</distortionK1>
      <distortionK2>0</distortionK2>
      <distortionK3>0</distortionK3>
      <distortionT1>0</distortionT1>
      <distortionT2>0</distortionT2>

      <!-- 相机内参（0 表示自动计算） -->
      <CxPrime>0</CxPrime>
      <Cx>0</Cx>
      <Cy>0</Cy>
      <focalLength>0</focalLength>
      <hackBaseline>0</hackBaseline>
    </plugin>
  </sensor>
</gazebo>
```

### 4.3 深度相机参数速查

| 参数 | 含义 | 建议值 |
|------|------|--------|
| `horizontal_fov` | 水平视角 | 1.047（60°） |
| `width × height` | 图像分辨率 | 640 × 480 |
| `near` | 最近可见距离 | 0.05m |
| `far` | 最远可见距离 | 3m |
| `update_rate` | 帧率 | 30 Hz |
| `pointCloudCutoff` | 点云最近裁剪 | 0.5m（太近当作没有） |
| `pointCloudCutoffMax` | 点云最远裁剪 | 3m（太远当作没有） |

---

## 5. 第三步：启动文件配置

你需要在启动 Gazebo 的时候加载初始化插件。通常在你的 `display.launch.py` 或专门的 `gazebo.launch.py` 中配置。

### Launch 文件

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    pkg_share = get_package_share_directory('你的功能包名')

    # 世界文件路径（SDF 格式，里面放了障碍物）
    world_path = os.path.join(pkg_share, 'world', 'my_world.sdf')

    # 启动 Gazebo
    # 关键：-s libgazebo_ros_init.so 初始化 ROS 接口
    #       -s libgazebo_ros_factory.so 允许 spawn 机器人模型
    gazebo = ExecuteProcess(
        cmd=['gazebo',
             '--verbose',
             '-s', 'libgazebo_ros_init.so',      # ← 必须加载！
             '-s', 'libgazebo_ros_factory.so',    # ← 必须加载！
             world_path],
        output='screen'
    )

    # 启动 robot_state_publisher（发布机器人的 TF）
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': open(
                os.path.join(pkg_share, 'urdf', 'robot.urdf')).read()}]
    )

    # 启动 RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_share, 'rviz', 'robot.rviz')]
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        rviz,
    ])
```

> 💡 **两个关键插件说明**：
>
> - `libgazebo_ros_init.so`：启动 Gazebo 和 ROS 之间的桥接
> - `libgazebo_ros_factory.so`：让你能用 ROS 命令在 Gazebo 中 spawn（生成）机器人

---

## 6. 第四步：CMakeLists.txt 和 package.xml

### CMakeLists.txt

确保 `world` 目录也被安装：

```cmake
cmake_minimum_required(VERSION 3.5)
project(你的功能包名)

find_package(ament_cmake REQUIRED)
# ... 其他依赖 ...

# 把所有需要的目录都安装到 share 目录
install(
  DIRECTORY
    launch
    config
    rviz
    world          # ← 别忘了加这个！世界文件也需要
    urdf
    meshes
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
```

### package.xml

确保 Gazebo ROS 相关的依赖都声明了：

```xml
<!-- Gazebo ROS 接口 -->
<exec_depend>gazebo_ros_pkgs</exec_depend>

<!-- 传感器消息 -->
<exec_depend>sensor_msgs</exec_depend>

<!-- 激光数据 -->
<exec_depend>laser_geometry</exec_depend>
```

---

## 7. 第五步：在 RViz 中验证传感器

编译运行后，打开 RViz 验证传感器是否正常工作。

### 7.1 检查话题列表

```bash
# 看看话题都出来了吗？
ros2 topic list

# 应该能看到：
# /scan                     ← 激光雷达数据
# /depth_camera/image_raw   ← 深度相机的图像
# /depth_camera/points      ← 深度相机的点云
```

### 7.2 检查每个话题有没有数据

```bash
# 检查激光雷达（看一下数据在不在刷新）
ros2 topic echo /scan --once

# 应该看到类似：
# header:
#   frame_id: lidar_link
# ranges: [1.5, 1.5, 1.5, inf, inf, 0.8, ...]  ← 360 个距离值

# 检查深度相机点云
ros2 topic echo /depth_camera/points --once

# 检查深度相机图像
ros2 topic hz /depth_camera/image_raw    # 看帧率是不是 30Hz
```

### 7.3 在 RViz 中可视化

启动 RViz 后，点击左下角 **Add** 按钮，添加以下显示：

| 显示类型 | 话题 | 注意事项 |
|----------|------|----------|
| **LaserScan** | `/scan` | Fixed Frame 选 `odom` 或 `lidar_link` |
| **PointCloud2** | `/depth_camera/points` | ⚠️ **Reliability Policy 改成 Best Effort** |
| **Image** | `/depth_camera/image_raw` | ⚠️ **Reliability Policy 改成 Best Effort** |

> ⚠️ **Best Effort 是什么？**
>
> ROS 2 默认使用 **Reliable** 传输（保证送达，但可能卡顿）。传感器数据量很大，如果每个数据包都要确认送达会拖慢系统，所以传感器数据一般用 **Best Effort**（尽力送达，丢了就丢了，下一帧马上来了）。
>
> **如果在 RViz 中看不到传感器数据，大概率是 Reliability Policy 没改！**

---

## 8. 第六步：把传感器传给 Nav2 代价地图

传感器自己跑通了还不够，你得告诉 Nav2："用这些数据来探测障碍物"。这就是 **Costmap 代价地图** 的工作。

### 8.1 全局代价地图（Global Costmap）

```yaml
# nav2_params.yaml
global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      robot_radius: 0.22
      resolution: 0.05

      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]

      # 障碍物层：用激光雷达数据来标记障碍物
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        observation_sources: scan              # ← 数据来源叫 "scan"（自定义名字）
        scan:
          topic: /scan                          # ← 对应激光雷达话题
          max_obstacle_height: 2.0              # 2m 以上的障碍物忽略
          clearing: True                        # 允许清除（障碍物走了就恢复为空地）
          marking: True                         # 允许标记（看到障碍物就标上去）
          data_type: "LaserScan"                # ← 数据类型
```

### 8.2 局部代价地图（Local Costmap）

局部代价地图可以同时用激光雷达 + 深度相机：

```yaml
# nav2_params.yaml
local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0                     # 局部地图更新要快！
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      rolling_window: true                      # 局部地图跟着机器人移动
      width: 3
      height: 3
      resolution: 0.05

      plugins: ["voxel_layer", "inflation_layer"]

      # 体素层：比 obstacle_layer 高级，支持 3D 数据
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        observation_sources: scan pointcloud    # ← 两个数据源！

        # 数据源 1：激光雷达
        scan:
          topic: /scan
          data_type: "LaserScan"
          max_obstacle_height: 2.0
          marking: True
          clearing: True

        # 数据源 2：深度相机点云
        pointcloud:
          topic: /depth_camera/points           # ← 深度相机的话题
          data_type: "PointCloud2"              # ← 数据类型变了！
          min_obstacle_height: 0.0              # 多矮都算障碍物
          max_obstacle_height: 2.0              # 2m 以上忽略
          marking: True
          clearing: True

      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        inflation_radius: 0.55
        cost_scaling_factor: 3.0
```

### 8.3 关键概念对比

| | obstacle_layer | voxel_layer |
|------|---------------|-------------|
| 处理什么数据 | 2D 的 LaserScan | 2D LaserScan **和** 3D PointCloud2 |
| 数据维度 | 2D | 3D → 投影到 2D |
| 适用场景 | 只有激光雷达 | 有激光雷达 + 深度相机/3D 雷达 |
| 推荐度 | 简单够用 | ✅ **推荐**（更灵活） |

---

## 9. 完整流程图

```
┌───────────────────────────────────────────────────────────┐
│                      URDF 机器人模型                       │
│                                                           │
│  ┌─────────────┐       ┌──────────────┐                  │
│  │ lidar_link  │       │ camera_link  │                  │
│  │ + ray插件   │       │ + depth插件  │                  │
│  └──────┬──────┘       └──────┬───────┘                  │
│         │                     │                           │
└─────────┼─────────────────────┼───────────────────────────┘
          │                     │
          ▼                     ▼
    ┌──────────┐        ┌────────────────┐
    │  /scan   │        │ /depth_camera  │
    │ LaserScan│        │   /image_raw   │    ← ROS 话题
    │          │        │   /points      │
    └────┬─────┘        └───────┬────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
    ┌─────────────────────────────────┐
    │     nav2_costmap_2d             │
    │  ┌───────────────────────────┐  │
    │  │ obstacle_layer / voxel   │  │    ← 代价地图订阅传感器
    │  │ → 标记障碍物             │  │
    │  └───────────────────────────┘  │
    └─────────────┬───────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────┐
    │     Planner / Controller        │    ← Nav2 用代价地图做规划
    │     → 规划路径，避开障碍物       │
    └─────────────────────────────────┘
```

---

## 10. 常见问题

### Q1: RViz 里看不到激光数据？

```
排查顺序：
1. ros2 topic list | grep scan          → /scan 存在吗？
2. ros2 topic echo /scan --once         → 有数据输出吗？
3. RViz 中 Fixed Frame 设对了吗？      → 设为 "odom" 或 "lidar_link"
4. RViz 中 Reliability Policy 改了吗？ → 改成 "Best Effort"
```

### Q2: 点云看不到？

```
1. ros2 topic echo /depth_camera/points --once  → 有没有数据？
2. RViz 中 Reliability Policy → 改成 Best Effort
3. RViz 中 PointCloud2 的 Style → 改成 "Points" 而不是 "Flat Squares"
4. 检查 Gazebo 中相机是否朝正确方向（可能对着墙了）
```

### Q3: Nav2 不避障？

```
调试步骤：
1. 确认 sensor 话题在正常工作（Q1/Q2 的方法）
2. 确认 nav2_params.yaml 中 observation_sources 的话题名正确
3. 确认 data_type 正确（LaserScan vs PointCloud2）
4. 确认 marking: True（一定要设为 true！）
5. RViz 中打开 Costmap 显示，看有没有红色的障碍物标记
```

### Q4: 传感器太多，插件加载卡顿？

```
- 把传感器的 <update_rate> 调低（如激光雷达 5Hz 就够了）
- 把深度相机分辨率降低（如 320×240）
- 点云裁剪距离缩小（pointCloudCutoffMax: 2.0 而不是 3.0）
```

### Q5: LIDAR 和深度相机该选哪个？

| 场景 | 推荐 |
|------|------|
| 室内、平面导航 | 只用 LIDAR 就够了 |
| 需要检测低矮障碍物（台阶、门槛） | LIDAR + 深度相机 |
| 需要检测悬挂障碍物（桌子边缘、吊灯） | LIDAR + 深度相机（3D 点云能检测高处的） |
| 仿真先跑通再说 | LIDAR 先搞定，再加深度相机 |

---

> ✍️ **学习心得**：给 Gazebo 机器人加传感器本质上就三步：
>
> 1. **URDF 定义**：link（传感器长什么样）+ joint（装在哪）+ plugin（怎么仿真）
> 2. **验证**：打开 RViz，添加显示，检查话题有没有数据
> 3. **接 Nav2**：在 nav2_params.yaml 的 costmap 层里声明传感器话题
>
> 最常犯的错误：① RViz 里 Reliability Policy 没改成 Best Effort ② nav2_params 里话题名写错 ③ 忘了把 world 目录加到 CMakeLists.txt。出问题时先查这三处。
