import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Check the backed-up original driver
_, stdout, _ = client.exec_command("grep -n 'def _build_tree\\|Save\\|save\\|Sequence\\|add_child\\|PublishStatus' /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py.bak.* 2>/dev/null", timeout=5)
print("=== Original _build_tree structure ===")
print(stdout.read().decode()[:2000])

# Also check the full nodes file
_, stdout, _ = client.exec_command("cat /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_nodes.py", timeout=5)
print("=== Full nodes file ===")
print(stdout.read().decode('utf-8', errors='ignore')[:2000])

client.close()
