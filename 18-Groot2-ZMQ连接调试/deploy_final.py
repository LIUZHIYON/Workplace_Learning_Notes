import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

LOCAL = r"C:\Users\29503\Desktop\AI学习笔记\18-Groot2-ZMQ连接调试\reminder_bt_driver_zmq.py"
REMOTE = "/home/cat/ros2_ws/src/robot_reminder_bt/robot_reminder_bt/reminder_bt_driver.py"

client.exec_command("pkill -f reminder_bt_driver; sleep 1", timeout=10)
sftp = client.open_sftp()
sftp.put(LOCAL, REMOTE)
sftp.close()
print("[OK] Uploaded")

cmd = (
    'bash -c \''
    'source /opt/ros/humble/setup.bash && '
    'source /home/cat/ros2_ws/install/setup.bash && '
    'export PYTHONPATH=/home/cat/ros2_ws/src/robot_reminder_bt:$PYTHONPATH && '
    'nohup python3 ' + REMOTE + ' '
    '--ros-args -p tick_interval_ms:=200 '
    '-p command_topic:=/robot/command '
    '-p response_topic:=/robot/command_response '
    '-p zmq_port:=1667 '
    '> /tmp/zmq_driver.log 2>&1 & echo DONE'
    '\''
)
_, stdout, _ = client.exec_command(cmd, timeout=10)
print("Launch:", stdout.read().decode().strip())
time.sleep(3)

_, stdout, _ = client.exec_command("ps aux | grep reminder_bt_driver | grep -v grep || true", timeout=5)
p = stdout.read().decode().strip()
print("Proc:", p[:200] if p else "(none)")

_, stdout, _ = client.exec_command("ss -tlnp | grep 1667 || true", timeout=5)
print("1667:", stdout.read().decode().strip() or "NOT LISTENING")

_, stdout, _ = client.exec_command("tail -30 /tmp/zmq_driver.log 2>/dev/null", timeout=5)
log = stdout.read().decode('utf-8', errors='ignore')
print("=== Log ===")
print(log[-2000:])

client.close()

if "(none)" in p:
    print("\nFAILED - see log above")
else:
    print("\n--- Testing ZMQ ---")
    import zmq, struct
    ctx = zmq.Context()
    s = ctx.socket(zmq.REQ)
    s.setsockopt(zmq.LINGER, 0)
    s.setsockopt(zmq.RCVTIMEO, 8000)
    s.setsockopt(zmq.SNDTIMEO, 5000)
    try:
        s.connect("tcp://192.168.1.191:1667")
        h = struct.pack("<BBL", 2, ord("T"), 1234)
        s.send_multipart([h, b""])
        r = s.recv_multipart()
        print("FULLTREE OK: {} parts, {}B".format(len(r), len(r[0])))
        h2 = struct.pack("<BBL", 2, ord("S"), 1235)
        s.send_multipart([h2, b""])
        r2 = s.recv_multipart()
        data = r2[1] if len(r2) >= 2 else r2[0][26:]
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
