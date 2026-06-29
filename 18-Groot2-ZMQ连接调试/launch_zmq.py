import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Try full bash login shell to get proper environment
cmd = (
    "bash -lc '"
    "cd /home/cat/ros2_ws && "
    "source /opt/ros/humble/setup.bash && "
    "source install/setup.bash && "
    "python3 -m robot_reminder_bt.reminder_bt_driver "
    "--ros-args -p tick_interval_ms:=200 "
    "-p command_topic:=/robot/command "
    "-p response_topic:=/robot/command_response "
    "-p zmq_port:=1667 "
    "&>/tmp/zmq_driver.log & echo PID:$! "
    "'"
)
print("Starting...")
_, stdout, _ = client.exec_command(cmd, timeout=10)
out = stdout.read().decode()
print("Output:", out[:200])
time.sleep(4)

# Check process
_, stdout, _ = client.exec_command("bash -lc 'ps aux | grep reminder_bt_driver | grep -v grep || true'", timeout=5)
proc = stdout.read().decode().strip()
print("Process:", proc[:200] if proc else "(not running)")

# Check port
_, stdout, _ = client.exec_command("ss -tlnp | grep 1667 || true", timeout=5)
print("Port 1667:", stdout.read().decode().strip() or "NOT LISTENING")

# Check log
_, stdout, _ = client.exec_command("cat /tmp/zmq_driver.log 2>/dev/null || echo no log", timeout=5)
log = stdout.read().decode('utf-8', errors='ignore')
print("=== Log ===")
print(log[-1500:] if log else "no log")

# If still not running, try using ros2 launch
if "(not running)" in proc:
    print("\nTrying ros2 launch...")
    cmd2 = (
        "bash -lc '"
        "cd /home/cat/ros2_ws && "
        "source /opt/ros/humble/setup.bash && "
        "source install/setup.bash && "
        "ros2 launch robot_reminder_bt reminder_bt.launch.py "
        "&>/tmp/zmq_launch.log & echo PID:$! "
        "'"
    )
    _, stdout, _ = client.exec_command(cmd2, timeout=10)
    out2 = stdout.read().decode()
    print("Launch:", out2[:200])
    time.sleep(5)
    
    _, stdout, _ = client.exec_command("ps aux | grep reminder_bt_driver | grep -v grep || true", timeout=5)
    proc2 = stdout.read().decode().strip()
    print("Process after launch:", proc2[:200] if proc2 else "(not running)")
    
    _, stdout, _ = client.exec_command("ss -tlnp | grep 1667 || true", timeout=5)
    print("Port 1667:", stdout.read().decode().strip() or "NOT LISTENING")
    
    # Check if colcon build is needed
    _, stdout, _ = client.exec_command("ls /home/cat/ros2_ws/install/robot_reminder_bt/lib/robot_reminder_bt/ 2>/dev/null", timeout=5)
    print("Installed scripts:", stdout.read().decode()[:500])

client.close()
