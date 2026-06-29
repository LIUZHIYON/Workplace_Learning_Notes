import paramiko, time, socket, sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.191", 22, "cat", "temppwd", timeout=10)

# 1. Kill existing driver
_, stdout, _ = client.exec_command("pkill -f reminder_bt_driver; sleep 1; echo killed", timeout=15)
print("Kill:", stdout.read().decode().strip())

# 2. Check service
_, stdout, _ = client.exec_command("systemctl is-active reminder.service 2>/dev/null || echo not-systemd", timeout=10)
svc = stdout.read().decode().strip()
print("Service:", svc)

# 3. If systemd, restart
if svc == "active":
    _, stdout, _ = client.exec_command("sudo systemctl restart reminder.service 2>&1", timeout=15)
    r = stdout.read().decode()
    print("Restart:", r or "OK")
    time.sleep(3)
    _, stdout, _ = client.exec_command("journalctl -u reminder.service --no-pager -n 30 2>/dev/null", timeout=10)
    print("=== Journal (last 30 lines) ===")
    print(stdout.read().decode()[-2000:])
else:
    # Try launching manually
    _, stdout, _ = client.exec_command(
        "cd /home/cat/ros2_ws && "
        "source /opt/ros/humble/setup.bash && source install/setup.bash && "
        "nohup python3 -m robot_reminder_bt.reminder_bt_driver "
        "--ros-args -p tick_interval_ms:=200 "
        "-p command_topic:=/robot/command "
        "-p relay_topic:=aipet/command_delivery "
        "-p response_topic:=/robot/command_response "
        "-p status_topic:=/robot/bt_status "
        "> /tmp/zmq_driver.log 2>&1 &",
        timeout=10
    )
    print("Manual launch done")
    time.sleep(2)

# 4. Check port 1667
_, stdout, _ = client.exec_command("ss -tlnp | grep 1667", timeout=5)
print("Port 1667:", stdout.read().decode().strip() or "NOT LISTENING")

# 5. Check process
_, stdout, _ = client.exec_command("ps aux | grep reminder_bt_driver | grep -v grep || true", timeout=5)
print("Process:", stdout.read().decode().strip() or "(not running)")

client.close()

# 6. Test ZMQ from local
print("\n--- Testing ZMQ connection ---")
import zmq, struct
ctx = zmq.Context()
s = ctx.socket(zmq.REQ)
s.setsockopt(zmq.LINGER, 0)
s.setsockopt(zmq.RCVTIMEO, 8000)
s.setsockopt(zmq.SNDTIMEO, 5000)
try:
    s.connect("tcp://192.168.1.191:1667")
    # FULLTREE
    header = struct.pack("<BBL", 2, ord("T"), 1234)
    s.send_multipart([header, b""])
    reply = s.recv_multipart()
    print("FULLTREE: {} parts, {} bytes".format(len(reply), len(reply[0]) if reply else 0))

    # STATUS
    header2 = struct.pack("<BBL", 2, ord("S"), 1235)
    s.send_multipart([header2, b""])
    reply2 = s.recv_multipart()
    data2 = reply2[0]
    cl = struct.unpack("<I", data2[22:26])[0]
    buf = data2[26:26+cl]
    status_names = {0:"IDLE", 1:"RUNNING", 2:"SUCCESS", 3:"FAILURE", 4:"SKIPPED"}
    statuses = {}
    offset = 0
    while offset + 3 <= len(buf):
        uid = struct.unpack("<H", buf[offset:offset+2])[0]
        st = buf[offset+2]
        statuses[uid] = st
        offset += 3
    print("STATUS: {} nodes".format(len(statuses)))
    for uid in sorted(statuses.keys()):
        print("  UID {}: {}".format(uid, status_names.get(statuses[uid], statuses[uid])))

except zmq.error.Again:
    print("ZMQ TIMEOUT")
except Exception as e:
    print("ZMQ Error:", e)
finally:
    s.close()
    ctx.term()
