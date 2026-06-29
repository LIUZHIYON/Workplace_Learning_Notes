import zmq, struct, time

def test_request(req_type_char, uid=1234):
    ctx = zmq.Context()
    s = ctx.socket(zmq.REQ)
    s.setsockopt(zmq.LINGER, 0)
    s.setsockopt(zmq.RCVTIMEO, 8000)
    s.setsockopt(zmq.SNDTIMEO, 5000)
    s.connect("tcp://192.168.1.191:1667")
    try:
        h = struct.pack("<BBL", 2, ord(req_type_char), uid)
        s.send_multipart([h, b""])
        r = s.recv_multipart()
        return r
    except zmq.error.Again:
        print("  TIMEOUT for request type", req_type_char)
        return None
    finally:
        s.close()
        ctx.term()

# FULLTREE
print("FULLTREE:")
r = test_request("T", 1)
if r and len(r) >= 2:
    print("  {} parts, frame0={}B, frame1={}B".format(len(r), len(r[0]), len(r[1])))
    xml = r[1].decode("utf-8", errors="ignore")
    print("  XML:", xml[:200])

# STATUS
print("\nSTATUS (3 polls):")
for i in range(3):
    print("  Poll #{}: ".format(i+1), end="")
    r = test_request("S", 10+i)
    if r and len(r) >= 2:
        data = r[1]
        sn = {0:"IDLE",1:"RUNNING",2:"SUCCESS",3:"FAILURE",4:"SKIPPED"}
        off = 0
        nodes = []
        while off + 3 <= len(data):
            uid = struct.unpack("<H", data[off:off+2])[0]
            status = data[off+2]
            nodes.append((uid, sn.get(status, status)))
            off += 3
        print("{} nodes".format(len(nodes)))
        for uid, sname in nodes:
            print("    UID {:>2}: {}".format(uid, sname))
    time.sleep(0.3)

# BLACKBOARD
print("\nBLACKBOARD:")
r = test_request("B", 100)
if r and len(r) >= 2:
    print("  Got {}B of msgpack data".format(len(r[1])))
    try:
        import msgpack
        bb = msgpack.unpackb(r[1])
        print("  Decoded:", bb)
    except:
        print("  (raw)")
