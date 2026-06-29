import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Check install directories
cmds = [
    "ls /home/cat/ros2_ws/install/robot_reminder_bt/ 2>/dev/null || echo no install",
    "ls /home/cat/ros2_ws/install/ 2>/dev/null",
    "find /home/cat -name setup.bash -path '*/install/*' 2>/dev/null",
    "find /home/cat -name '__init__.py' -path '*/robot_reminder_bt*' 2>/dev/null | head -5",
    "cat /home/cat/.bashrc | grep -i 'ros2\\|ros\\|install' 2>/dev/null || true",
    "ls -la /home/cat/ros2_ws/src/robot_reminder_bt/setup.py 2>/dev/null",
]
for c in cmds:
    print(f"$ {c}")
    _, stdout, _ = client.exec_command(c, timeout=10)
    out = stdout.read().decode('utf-8', errors='ignore')
    print(out[:300])
    print()

client.close()
