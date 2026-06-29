import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Check service definition
_, stdout, _ = client.exec_command("cat /etc/systemd/system/reminder.service 2>/dev/null", timeout=10)
print("=== reminder.service ===")
print(stdout.read().decode()[:2000])

# Check board-ws-client service
_, stdout, _ = client.exec_command("systemctl cat board-ws-client.service 2>/dev/null", timeout=10)
s = stdout.read().decode()
if s:
    print("=== board-ws-client.service ===")
    print(s[:2000])

# Check launch file
_, stdout, _ = client.exec_command("ls /home/cat/ros2_ws/src/robot_reminder_bt/launch/ 2>/dev/null || echo no launch", timeout=5)
print("=== Launch dir ===")
print(stdout.read().decode()[:500])

# Check setup.py or entry points
_, stdout, _ = client.exec_command("cat /home/cat/ros2_ws/src/robot_reminder_bt/setup.py 2>/dev/null || echo no setup.py", timeout=5)
print("=== setup.py ===")
print(stdout.read().decode()[:1000])

# Check backup timestamps
_, stdout, _ = client.exec_command("ls -la /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/*.bak* 2>/dev/null", timeout=5)
print("=== Backups ===")
print(stdout.read().decode()[:500])

# Check for groot2 server running
_, stdout, _ = client.exec_command("ps aux | grep -i groot 2>/dev/null || echo no groot", timeout=5)
print("=== Groot processes ===")
print(stdout.read().decode()[:500])

# Check python processes on ports
_, stdout, _ = client.exec_command("ss -tlnp | grep python 2>/dev/null || echo no python listening", timeout=5)
print("=== Python listening ports ===")
print(stdout.read().decode()[:500])

client.close()
