import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Get the FULL original backup driver to see the complete tree
_, stdout, _ = client.exec_command("cat /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py.bak.* 2>/dev/null | head -100", timeout=10)
print("=== Original driver (first 100 lines) ===")
print(stdout.read().decode('utf-8', errors='ignore')[:1500])

# Get the _build_tree section
_, stdout, _ = client.exec_command("cat /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py.bak.* 2>/dev/null | sed -n '230,275p'", timeout=10)
print()
print("=== _build_tree ===")
print(stdout.read().decode('utf-8', errors='ignore')[:2000])

client.close()
