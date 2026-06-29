import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# Upload the file
sftp = client.open_sftp()
sftp.put(r"C:\Users\29503\Desktop\AI学习笔记\18-Groot2-ZMQ连接调试\reminder_bt_driver_zmq.py",
         "/home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py")
sftp.close()
print("[OK] Uploaded")

# Kill old process
client.exec_command("pkill -f reminder_bt_driver; pkill -f zmq_driver", timeout=10)
time.sleep(1)

# Create a startup script on the board
startup_script = (
    "#!/bin/bash\n"
    "export HOME=/home/cat\n"
    "source /opt/ros/humble/setup.bash\n"
    "source /home/cat/ros2_ws/install/setup.bash\n"
    "export PYTHONPATH=/home/cat/ros2_ws/src/robot_reminder_bt:$PYTHONPATH\n"
    "cd /home/cat/ros2_ws\n"
    "exec python3 /home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py\n"
)

stdin, stdout, stderr = client.exec_command("cat > /tmp/run_zmq.sh", timeout=5)
stdin.write(startup_script)
stdin.channel.shutdown_write()

client.exec_command("chmod +x /tmp/run_zmq.sh", timeout=5)

# Launch with nohup - use /bin/bash to ensure proper sourcing
_, stdout, _ = client.exec_command(
    "nohup /bin/bash /tmp/run_zmq.sh > /tmp/zmq_driver.log 2>&1 & echo PID:$!",
    timeout=10
)
pid = stdout.read().decode().strip()
print("Launched PID:", pid)
time.sleep(4)

# Check
_, stdout, _ = client.exec_command("ps aux | grep reminder_bt_driver | grep -v grep || true", timeout=5)
p = stdout.read().decode().strip()
print("Proc:", p[:200] if p else "(none)")

_, stdout, _ = client.exec_command("ss -tlnp | grep 1667 || true", timeout=5)
print("1667:", stdout.read().decode().strip() or "NOT LISTENING")

_, stdout, _ = client.exec_command("tail -20 /tmp/zmq_driver.log 2>/dev/null", timeout=5)
log = stdout.read().decode("utf-8", errors="ignore")
print("=== Log ===")
print(log[-2000:])

client.close()

# Test ZMQ
print("\n--- Test ZMQ ---")
if "LISTEN" in stdout.read().decode() if False else True:
    import zmq, struct
    ctx = zmq.Context()
    s = ctx.socket(zmq.REQ)
    s.setsockopt(zmq.LINGER, 0)
    s.setsockopt(zmq.RCVTIMEO, 6000)
    s.setsockopt(zmq.SNDTIMEO, 4000)
    try:
        s.connect("tcp://192.168.1.191:1667")
        h = struct.pack("<BBL", 2, ord("T"), 1)
        s.send_multipart([h, b""])
        r = s.recv_multipart()
        print("FULLTREE OK: {} parts, {}B".format(len(r), len(r[0])))

        h2 = struct.pack("<BBL", 2, ord("S"), 2)
        s.send_multipart([h2, b""])
        r2 = s.recv_multipart()
        data = r2[1]
        sn = {0:"IDLE",1:"RUNNING",2:"SUCCESS",3:"FAILURE",4:"SKIPPED"}
        off = 0
        while off + 3 <= len(data):
            uid = struct.unpack("<H", data[off:off+2])[0]
            st = data[off+2]
            print("  UID {}: {}".format(uid, sn.get(st, st)))
            off += 3
    except zmq.error.Again:
        print("ZMQ TIMEOUT")
    except Exception as e:
        print("Error:", e)
    finally:
        s.close()
        ctx.term()
