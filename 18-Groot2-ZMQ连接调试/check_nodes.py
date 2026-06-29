import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Check the nodes file for SavePersistence
_, stdout, _ = client.exec_command("grep -n 'class\\|__all__' /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_nodes.py 2>/dev/null", timeout=5)
print("=== Classes defined ===")
print(stdout.read().decode()[:1000])

# Check file size
_, stdout, _ = client.exec_command("wc -l /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_nodes.py", timeout=5)
print("=== File size ===")
print(stdout.read().decode())

# Check the bt_engine too
_, stdout, _ = client.exec_command("grep -n '^class\\|def execute' /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/bt_engine.py 2>/dev/null", timeout=5)
print("=== bt_engine classes ===")
print(stdout.read().decode()[:500])

client.close()
