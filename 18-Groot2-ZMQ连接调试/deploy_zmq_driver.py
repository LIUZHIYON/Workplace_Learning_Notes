# deploy script - upload reminder_bt_driver_zmq.py to board
import paramiko, sys, os, time

HOST = "192.168.1.191"
USER = "cat"
PASS = "temppwd"
PORT = 22

LOCAL_FILE = r"C:\Users\29503\Desktop\AI学习笔记\18-Groot2-ZMQ连接调试\reminder_bt_driver_zmq.py"
REMOTE_PATH = "/home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py"

def run_ssh(client, cmd, timeout=15):
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    return exit_code, out, err

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USER, PASS, timeout=10)
    print("[OK] SSH connected")

    # 1. Check current file
    ec, out, err = run_ssh(client, "ls -la " + REMOTE_PATH)
    print("Current:", out[:100] if out else err[:100])

    # 2. Backup original
    backup_name = REMOTE_PATH + ".bak." + str(int(time.time()))
    ec, out, err = run_ssh(client, "cp " + REMOTE_PATH + " " + backup_name)
    print("Backup:", backup_name)

    # 3. Upload new file
    sftp = client.open_sftp()
    sftp.put(LOCAL_FILE, REMOTE_PATH)
    sftp.close()
    print("[OK] File uploaded")

    # 4. Verify
    ec, out, err = run_ssh(client, "wc -l " + REMOTE_PATH)
    print("Lines:", out)

    # 5. Check pyzmq
    ec, out, err = run_ssh(client, "python3 -c 'import zmq; print(zmq.__version__)'")
    print("pyzmq:", out or err)

    # 6. Check msgpack
    ec, out, err = run_ssh(client, "python3 -c 'import msgpack; print(msgpack.__version__)'")
    print("msgpack:", out or err)

    # 7. Check running processes
    ec, out, err = run_ssh(client, "ps aux | grep reminder_bt_driver | grep -v grep || true")
    print("BT processes:")
    for line in out.split("\n") if out else ["(none)"]:
        print("  " + line)

    # 8. Check if there's a systemd service for reminder
    ec, out, err = run_ssh(client, "systemctl list-units --type=service --state=running 2>/dev/null | grep -i reminder || true")
    print("Systemd services:", out or "(none)")

    # 9. Check ros2 launch
    ec, out, err = run_ssh(client, "ps aux | grep -E '[r]os2|[l]aunch' | head -5 || true")
    print("ROS2 processes:")
    for line in out.split("\n") if out else ["(none)"]:
        print("  " + line)

    client.close()
    print("\n[OK] Done! Restart the ROS2 node or service to apply.")

    print("\n--- Manual restart commands (SSH into board) ---")
    print("  sudo systemctl restart robot_reminder_bt  # if systemd service")
    print("  # or pkill -f reminder_bt_driver; ros2 run robot_reminder_bt reminder_bt_driver")
    print("  # or ros2 launch robot_reminder_bt reminder_bt.launch.py")

except paramiko.AuthenticationException:
    print("[FAIL] SSH auth failed (wrong password?)")
except paramiko.SSHException as e:
    print("[FAIL] SSH error:", e)
except Exception as e:
    print("[FAIL] Error:", e)
    import traceback
    traceback.print_exc()
