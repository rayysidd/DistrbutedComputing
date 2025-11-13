import socket
import threading
import json
import argparse
import time
import sys

# --- Utility: send JSON msg (newline-terminated) ---
def send_msg(addr, msg, timeout=2):
    try:
        s = socket.create_connection(addr, timeout=timeout)
        s.sendall((json.dumps(msg) + "\n").encode())
        s.close()
        return True
    except Exception:
        return False

class Node:
    def __init__(self, pid, nodes):
        self.pid = pid
        self.nodes = {n["pid"]:(n["host"], n["port"]) for n in nodes}
        self.host, self.port = self.nodes[pid]
        self.coordinator = None
        self.alive = True
        self.lock = threading.Lock()
        self.server = None

    # --- server: accept incoming connections and handle messages ---
    def start_server(self):
        def handler(conn, addr):
            try:
                data = b""
                while True:
                    part = conn.recv(4096)
                    if not part:
                        break
                    data += part
                text = data.decode().strip()
                if not text:
                    return
                for line in text.splitlines():
                    try:
                        msg = json.loads(line)
                    except Exception:
                        continue
                    self.handle_msg(msg)
            finally:
                conn.close()

        def server_thread():
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            self.server = s
            print(f"[{self.pid}] Listening on {self.host}:{self.port}")
            while self.alive:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=handler, args=(conn, addr), daemon=True).start()
                except Exception:
                    break
            s.close()

        t = threading.Thread(target=server_thread, daemon=True)
        t.start()

    # --- message handler ---
    def handle_msg(self, msg):
        typ = msg.get("type")
        src = msg.get("from")

        if typ == "ELECTION":
            # reply OK if receiver has higher pid than sender
            print(f"[{self.pid}] Received ELECTION from {src}")
            if self.pid > src:
                # send OK back to sender
                addr = self.nodes[src]
                print(f"[{self.pid}] Sending OK to {src}")
                send_msg(addr, {"type":"OK","from":self.pid})
                # start own election
                threading.Thread(target=self.start_election, daemon=True).start()

        elif typ == "OK":
            print(f"[{self.pid}] Received OK from {src}")
            # flag that someone higher is alive - store in a small variable
            with self.lock:
                self._got_ok = True

        elif typ == "COORDINATOR":
            newc = msg.get("coordinator")
            with self.lock:
                self.coordinator = newc
            print(f"[{self.pid}] Received COORDINATOR message: new coordinator = {newc}")

        elif typ == "PING":
            # reply PONG
            send_msg(self.nodes[src], {"type":"PONG","from":self.pid})

        elif typ == "PONG":
            # heartbeat response; ignore details here
            pass

    # --- election process (Bully) ---
    def start_election(self):
        print(f"[{self.pid}] Initiating election...")
        higher = [p for p in self.nodes if p > self.pid]

        # reset ok flag
        with self.lock:
            self._got_ok = False

        # send ELECTION to all higher processes
        for p in higher:
            addr = self.nodes[p]
            send_msg(addr, {"type":"ELECTION","from":self.pid})

        # wait for OKs for a short time
        time.sleep(2)
        with self.lock:
            got = getattr(self, "_got_ok", False)

        if not got:
            # no OK received -> become coordinator
            with self.lock:
                self.coordinator = self.pid
            print(f"[{self.pid}] I am the new COORDINATOR")
            # broadcast coordinator msg
            for p, addr in self.nodes.items():
                if p == self.pid:
                    continue
                send_msg(addr, {"type":"COORDINATOR","from":self.pid, "coordinator":self.pid})
        else:
            print(f"[{self.pid}] Got OK from a higher process; waiting for COORDINATOR announcement...")

    # --- heartbeat thread: check coordinator every few seconds ---
    def heartbeat_loop(self):
        def loop():
            while self.alive:
                time.sleep(3)
                with self.lock:
                    coord = self.coordinator
                if coord is None or coord == self.pid:
                    continue
                addr = self.nodes.get(coord)
                if not addr:
                    continue
                ok = send_msg(addr, {"type":"PING","from":self.pid}, timeout=1)
                if not ok:
                    # coordinator not responding
                    print(f"[{self.pid}] Coordinator {coord} not responding -> starting election")
                    threading.Thread(target=self.start_election, daemon=True).start()
        threading.Thread(target=loop, daemon=True).start()

    # --- initial startup election ---
    def startup(self):
        # short delay to let servers start
        time.sleep(1)
        print(f"[{self.pid}] Starting initial election")
        self.start_election()

    def stop(self):
        self.alive = False
        # close server socket to exit accept()
        if self.server:
            try:
                self.server.close()
            except Exception:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    args = parser.parse_args()

    # load nodes
    with open("nodes.json") as f:
        nodes = json.load(f)

    pids = [n["pid"] for n in nodes]
    if args.pid not in pids:
        print("PID not in nodes.json")
        sys.exit(1)

    node = Node(args.pid, nodes)
    try:
        node.start_server()
        node.heartbeat_loop()
        node.startup()
        # keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"[{node.pid}] Shutting down")
        node.stop()
        time.sleep(0.5)