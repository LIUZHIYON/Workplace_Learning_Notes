import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Get the _collect_node_statuses section
_, stdout, _ = client.exec_command(
    "cat /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py.bak.* 2>/dev/null "
    "| sed -n '195,240p'",
    timeout=10
)
print("=== _collect_node_statuses / _build_xml ===")
print(stdout.read().decode('utf-8', errors='ignore')[:3000])

# Get the _assign_uids or similar
_, stdout, _ = client.exec_command(
    "cat /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py.bak.* 2>/dev/null "
    "| sed -n '160,195p'",
    timeout=10
)
print()
print("=== Init section after tree build ===")
print(stdout.read().decode('utf-8', errors='ignore')[:2000])

client.close()
