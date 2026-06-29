import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Use bash -c with explicit source of ros2 + install, then run source file directly
cmd = (
    'bash -c \''
    'source /opt/ros/humble/setup.bash && '
    'source /home/cat/ros2_ws/install/setup.bash && '
    'export PYTHONPATH=/home/cat/ros2_ws/src/robot_reminder_bt:$PYTHONPATH && '
    'nohup python3 /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py '
    '--ros-args -p tick_interval_ms:=200 '
    '-p command_topic:=/robot/command '
    '-p response_topic:=/robot/command_response '
    '-p zmq_port:=1667 '
    '> /tmp/zmq_driver.log 2>&1 &'
    ' echo STARTED'
    '\''
)
print("Running with full env...")
_, stdout, _ = client.exec_command(cmd, timeout=10)
out = stdout.read().decode().strip()
print("Output:", out)
time.sleep(4)

_, stdout, _ = client.exec_command("ps aux | grep reminder_bt_driver | grep -v grep || true", timeout=5)
proc = stdout.read().decode().strip()
print("Process:", proc[:300] if proc else "(not running)")

_, stdout, _ = client.exec_command("ss -tlnp | grep 1667 || true", timeout=5)
print("Port 1667:", stdout.read().decode().strip() or "NOT LISTENING")

_, stdout, _ = client.exec_command("tail -40 /tmp/zmq_driver.log 2>/dev/null", timeout=5)
log = stdout.read().decode('utf-8', errors='ignore')
print("=== Log ===")
print(log[-2000:])

client.close()
