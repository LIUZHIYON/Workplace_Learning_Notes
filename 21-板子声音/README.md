# RK3576 开发板 — 音频调试指令集

> 板子 IP: `192.168.1.209` | 系统: `armbian` | 声卡: `rockchip,aw883xx` (aw883xx 功放)
> 整理日期: 2026-06-30

---

## 目录

- [一、检查音频状态](#一检查音频状态)
- [二、调整音量](#二调整音量)
- [三、ROS2 语音管线](#三ros2-语音管线)
- [四、一键检查脚本](#四一键检查脚本)
- [五、排查思路](#五排查思路)

---

## 一、检查音频状态

### 1.1 ALSA 混音器状态

```bash
# 查看所有 ALSA 控制器
amixer scontrols

# 查看所有控制器详细信息
amixer scontents | head -40

# 查看具体某个控制器
amixer sget 'Headphone'
amixer sget 'Speaker'
amixer sget 'aw_dev_0_switch'         # 功放开关 (Enable/Disable)
amixer sget 'aw_dev_0_rx_volume'      # 功放音量 (0-1023)
```

| 控制器名 | 说明 | 典型值 |
|---------|------|--------|
| `Headphone` | 耳机通道开关 | 应 `[on]` |
| `Speaker` | 喇叭通道开关 | 应 `[on]` |
| `aw_dev_0_switch` | aw883xx 功放使能 | 应 `'Enable'` |
| `aw_dev_0_rx_volume` | 功放音量 (0-1023) | 921 ≈ 90% |

### 1.2 PulseAudio 状态

```bash
pactl list sinks short           # 列出音频输出设备
pactl get-sink-volume 0          # 当前音量 (% / dB)
pactl get-sink-mute 0            # 是否静音 (0=否, 1=是)
```

### 1.3 查看声卡设备

```bash
# 播放设备
aplay -l

# 录音设备
arecord -l

# 声卡信息
cat /proc/asound/cards
```

---

## 二、调整音量

### 2.1 ALSA 混音器（硬件级）

```bash
# 开关控制
amixer sset 'Headphone' unmite           # 取消静音
amixer sset 'Headphone' mute             # 静音
amixer sset 'Speaker' unmute
amixer sset 'aw_dev_0_switch' on         # 打开功放
amixer sset 'aw_dev_0_switch' off        # 关闭功放

# 音量控制（百分比）
amixer sset 'aw_dev_0_rx_volume' 90%     # 设功放 90%

# 音量控制（数值 0-1023）
amixer sset 'aw_dev_0_rx_volume' 921     # 921 ≈ 90%
```

### 2.2 PulseAudio（系统级）

```bash
pactl set-sink-volume 0 90%              # 设音量为 90%
pactl set-sink-mute 0 0                  # 取消静音
pactl set-sink-mute 0 1                  # 静音
```

### 2.3 ROS2 audio_node（应用级）

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

# 设音量（整数 0-100）
ros2 service call /audio/set_volume robot_audio_node/srv/SetVolume '{volume: 90}'

# 获取音量
ros2 service call /audio/get_volume robot_audio_node/srv/GetVolume '{}'
```

> **注意**: `SetVolume` 的 `volume` 字段类型是 **int32**（不是 float），范围 0-100。传 `0.9` 会被截断成 `0`！

---

## 三、ROS2 语音管线

### 3.1 三个声音节点

| 节点 | 包名 | 说明 |
|------|------|------|
| `/voice_bridge` | `robot_voice_bridge` | Action 服务器，调度 TTS 合成 + 音频播放 |
| `/tts_node` | `robot_doubao_tts_node` | 豆包 TTS 合成（文本→PCM） |
| `/robot_audio_node` | `robot_audio_node` | ALSA 音频播放（解码 + 出声） |

### 3.2 启动脚本

```bash
# 一键启动三个声音节点
bash /home/cat/start_voice.sh

# 该脚本内容：
#   ros2 launch robot_voice_bridge voice_bridge.launch.py &
#   ros2 launch robot_doubao_tts_node tts.launch.py &
#   ros2 launch robot_audio_node robot_audio_node.launch.py &
```

### 3.3 检查管线是否正常运行

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

# 查看节点列表
ros2 node list | grep -iE 'voice|audio|tts'

# 查看 Action Server（应有 /voice/speak）
ros2 action list

# 查看音频相关话题
ros2 topic list | grep -iE 'voice|audio|tts'

# 查看某个节点的详情
ros2 node info /voice_bridge
ros2 node info /robot_audio_node
```

### 3.4 管线数据流

```
reminder_bt_driver
    ↓ Action: /voice/speak
voice_bridge (C++ Action Server)
    ↓ pub: /tts/text
tts_node (豆包TTS)
    ↓ pub: /tts/audio (PCM)
voice_bridge → 拼装 WAV → pub: /audio/audio_cmd
    ↓
robot_audio_node (FFmpeg + ALSA)
    ↓
喇叭出声 🔊
```

---

## 四、一键检查脚本

SSH 登上去后直接粘贴执行：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

echo "=== ROS2 Nodes ==="
ros2 node list | grep -iE 'voice|audio|tts'

echo "=== Action ==="
ros2 action list

echo "=== Volume (ROS2) ==="
ros2 service call /audio/get_volume robot_audio_node/srv/GetVolume '{}' 2>&1 | tail -3

echo "=== ALSA Mixer ==="
amixer sget 'Headphone' | head -3
amixer sget 'Speaker' | head -3
amixer sget 'aw_dev_0_switch' | head -3
amixer sget 'aw_dev_0_rx_volume' | head -3

echo "=== PulseAudio ==="
pactl get-sink-volume 0
pactl get-sink-mute 0

echo "=== Audio Hardware Test ==="
WAV=$(find /home/cat/reminder_system/audio -name '*.wav' -type f 2>/dev/null | head -1)
if [ -n "$WAV" ]; then
    aplay -D plughw:0,0 "$WAV" &
    sleep 1 && echo "Playing..."
    wait
fi
```

---

## 五、排查思路

```
喇叭不响？按顺序排查：
┌─────────────────────────────────┐
│ 1. aplay test.wav               │ ← 硬件出不出声？
│    ├── 有声 → 硬件没问题        │
│    └── 无声 → 检查混音器/功放   │
├─────────────────────────────────┤
│ 2. amixer 检查混音器            │ ← Headphone/Speaker 开了没？
│    ├── [on] → 继续              │
│    └── [off] → amixer unmute    │
├─────────────────────────────────┤
│ 3. amixer 检查 aw883xx 功放     │ ← 功放开了没？
│    ├── Enable → 继续            │
│    └── Disable → amixer on      │
├─────────────────────────────────┤
│ 4. pactl 检查 PulseAudio        │ ← 系统音量静音了没？
│    ├── mute=0 volume>0 → 继续    │
│    └── 有问题 → pactl set       │
├─────────────────────────────────┤
│ 5. ROS2 节点都活着？             │ ← voice_bridge / tts_node / audio_node
│    ├── 都在 → 继续              │
│    └── 缺 → bash start_voice.sh │
├─────────────────────────────────┤
│ 6. ROS2 volume 设了没？          │ ← 应用层音量
│    ├── volume=90 → OK            │
│    └── volume=0 → service call   │
├─────────────────────────────────┤
│ 7. Action 链路通吗？             │ ← /voice/speak 存在？
│    └── 检查 ros2 action list     │
└─────────────────────────────────┘
```

---

## 附：常见问题

### Q: SetVolume 传了 0.9 但 volume 变成 0？
**A:** `volume` 字段是 `int32` 类型，传 float 会被截断。应传整数：
```bash
# 正确 ✓
ros2 service call /audio/set_volume robot_audio_node/srv/SetVolume '{volume: 90}'

# 错误 ✗ (volume=0)
ros2 service call /audio/set_volume robot_audio_node/srv/SetVolume '{volume: 0.9}'
```

### Q: 启动 start_voice.sh 后发现 Headphone 是 off？
**A:** 启动脚本只启动 ROS2 节点，不管 ALSA 混音器。开机后需额外执行：
```bash
amixer sset 'Headphone' unmute
amixer sset 'aw_dev_0_switch' on
pactl set-sink-volume 0 90%
```

### Q: aplay 能播，但 ROS2 动作不响？
**A:** 检查 ROS2 音量参数。`robot_audio_node` 内部有独立的 volume 参数（默认 1.0），如果被设成 0 则不出声。另外确认管线话题是否连通（`ros2 topic echo /audio/audio_cmd`）。
