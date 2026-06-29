"""Download modified files from board to local git repo"""
import paramiko, os, shutil

REMOTE_WS = "/home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt"
LOCAL_WS = r"E:\LuBanCat\BT_ros2\reminder_codex-1.1\robot_reminder_bt"

FILES = [
    "reminder_bt_driver.py",
    "reminder_bt_nodes.py",
    "bt_engine.py",
]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)
sftp = client.open_sftp()

for fname in FILES:
    remote_path = f"{REMOTE_WS}/{fname}"
    local_path = f"{LOCAL_WS}\\{fname}"
    
    try:
        sftp.stat(remote_path)
    except FileNotFoundError:
        print(f"[SKIP] {fname} - not found on board")
        continue
    
    sftp.get(remote_path, local_path)
    print(f"[OK] {fname} downloaded to local")

sftp.close()
client.close()
print("\nDone! Now commit in git:")
print(f"  cd {LOCAL_WS}")
print("  git add -A")
print('  git commit -m "feat: embed ZMQ Groot2 monitor server into driver"')
print("  git push")
