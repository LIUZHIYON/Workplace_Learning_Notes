import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Get the full _zmq_loop section from the backup
_, stdout, _ = client.exec_command(
    "cat /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py.bak.* 2>/dev/null "
    "| sed -n '280,400p'",
    timeout=10
)
print("=== ZMQ section ===")
print(stdout.read().decode('utf-8', errors='ignore')[:3000])

client.close()
