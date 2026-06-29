import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Check the installed executable
_, stdout, _ = client.exec_command("ls /home/cat/ros2_ws/install/robot_reminder_bt/lib/robot_reminder_bt/", timeout=5)
print("Installed executables:")
print(stdout.read().decode()[:500])

# Run the new driver directly (not via module), with PYTHONPATH set
cmd = (
    "cd /home/cat/ros2_ws && "
    "export PYTHONPATH=/home/cat/ros2_ws/src/robot_reminder_bt:$PYTHONPATH && "
    "export PYTHONPATH=/home/cat/ros2_ws/install/robot_reminder_bt/lib/python3.10/site-packages:$PYTHONPATH && "
    "/usr/bin/python3 /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py "
    "&>/tmp/zmq_driver.log & echo PID:$!"
)
print("Running: ", cmd[:80])
_, stdout, _ = client.exec_command(cmd, timeout=10)
out = stdout.read().decode().strip()
print("PID:", out)
time.sleep(4)

# Check process
_, stdout, _ = client.exec_command("ps aux | grep reminder_bt_driver | grep -v grep || true", timeout=5)
proc = stdout.read().decode().strip()
print("Process:", proc[:300] if proc else "(not running)")

# Check port
_, stdout, _ = client.exec_command("ss -tlnp | grep 1667 || true", timeout=5)
print("Port 1667:", stdout.read().decode().strip() or "NOT LISTENING")

# Check log
_, stdout, _ = client.exec_command("tail -30 /tmp/zmq_driver.log 2>/dev/null || echo no log", timeout=5)
log = stdout.read().decode('utf-8', errors='ignore')
print("=== Log ===")
print(log[-2000:] if log else "no log")

client.close()
