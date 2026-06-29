# 快速参考

## 启动顺序

```
1. 板子启动服务器
   ssh cat@192.168.1.70
   cd ~/groot2_bridge
   pkill -f 'groot2_server'
   nohup python3 -u groot2_server.py > /tmp/g2.log 2>&1 &

2. 本地启动 BehaviorTreeMonitor
   cd E:\LuBanCat\BT_ros2\BehaviorTreeMonitor
   python main.py

3. 连接
   Host: 192.168.1.70
   Port: 1667
```

## 常用命令

```bash
# 检查服务器
ssh cat@192.168.1.70 "ss -tlnp | grep 1667"

# 查看日志
ssh cat@192.168.1.70 "tail -20 /tmp/g2.log"

# 创建测试提醒
curl -X POST http://192.168.1.70:5000/api/reminders \
  -H "Content-Type: application/json" \
  -d '{"content":"测试播报","reminder_time":"2026-06-26 20:00:00"}'

# 查看待触发提醒
curl -s http://192.168.1.70:5000/api/reminders?status=pending
```

## 排查

| 现象 | 原因 | 解决 |
|------|------|------|
| connect timeout | 板子服务器没启动 | `pkill -f groot2_server` 后重启 |
| send err, recreating | ZMQ 状态死锁 | 自动恢复（已修复） |
| 节点不变色 | 没触发提醒 | 创建一条提醒 |
| js: 连接失败 | Host/Port 写错 | 确认是 192.168.1.70:1667 |
