import os
import socket
import threading
import json
import argparse
import time
import sys

def send_msg(addr, msg, timeout=2):
    try:
        s = socket.create_connection(addr, timeout=timeout)
        s.sendall((json.dumps(msg) + "\n").encode())
        s.close()
        return True
    except Exception:
        return False

class RingNode:
    def __init__(self, pid, nodes):
        # nodes is list of dicts sorted by pid ascending as provided in nodes.json
        self.pid = pid
        self.nodes_list = nodes[:]  # preserve order in file
        self.nodes_by_pid = {n["pid"]:(n["host"], n["port"]) for n in nodes}
        self.host, self.port = self.nodes_by_pid[pid]
        # find index & next node in ring
        idx = next(i for i, n in enumerate(self.nodes_list) if n["pid"] == pid)
        self.idx = idx
        self.next_node = self.nodes_list[(idx + 1) % len(self.nodes_list)]
        self.coordinator = None
        self.alive = True
        self.server = None
        self.lock = threading.Lock()

    # find next reachable node starting after start_index (inclusive)
    def _find_next_reachable(self, start_index=None, attempts=None):
        if attempts is None:
            attempts = len(self.nodes_list) - 1
        if start_index is None:
            start_index = (self.idx + 1) % len(self.nodes_list)
        n = len(self.nodes_list)
        i = start_index
        tried = 0
        while tried < attempts:
            node = self.nodes_list[i]
            if node["pid"] != self.pid:
                ok = send_msg((node["host"], node["port"]),
                              {"type":"PING", "from":self.pid, "from_host":self.host, "from_port":self.port},
                              timeout=1)
                if ok:
                    return node, i
            i = (i + 1) % n
            tried += 1
        return None, None

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
            print(f"[{self.pid}] Listening on {self.host}:{self.port} | next -> {self.next_node['pid']} @ {self.next_node['host']}:{self.next_node['port']}")
            while self.alive:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=handler, args=(conn, addr), daemon=True).start()
                except Exception:
                    break
            s.close()

        threading.Thread(target=server_thread, daemon=True).start()

    def handle_msg(self, msg):
        typ = msg.get("type")
        if typ == "ELECTION":
            origin = msg.get("origin")
            ids = msg.get("ids", [])
            print(f"[{self.pid}] Received ELECTION from ring (origin={origin}) ids={ids}")
            # append own pid if not present
            if self.pid not in ids:
                ids.append(self.pid)
            # forward unless back to origin
            if origin == self.pid:
                # election complete at origin
                print(f"[{self.pid}] Election message returned to origin. participants={ids}")
                winner = max(ids)
                # announce coordinator around the ring (forward to next reachable)
                self.coordinator = winner
                node, index = self._find_next_reachable(start_index=(self.idx + 1) % len(self.nodes_list))
                if node:
                    send_msg((node['host'], node['port']),
                             {"type":"COORDINATOR", "origin":self.pid, "coordinator":winner})
                    print(f"[{self.pid}] ELECTION result -> coordinator = {winner}, forwarded to {node['pid']}")
                else:
                    print(f"[{self.pid}] No reachable node to forward COORDINATOR; staying coordinator = {winner}")
            else:
                # forward to next reachable node
                node, index = self._find_next_reachable(start_index=(self.idx + 1) % len(self.nodes_list))
                if node:
                    send_msg((node['host'], node['port']),
                             {"type":"ELECTION", "origin":origin, "ids":ids})
                    print(f"[{self.pid}] Forwarded ELECTION to {node['pid']}")
                else:
                    # can't forward -> assume we are the only reachable participant, finish election locally
                    print(f"[{self.pid}] No reachable node to forward ELECTION; concluding election locally")
                    winner = max(ids)
                    self.coordinator = winner
                    print(f"[{self.pid}] ELECTION result -> coordinator = {winner}")

        elif typ == "COORDINATOR":
            winner = msg.get("coordinator")
            origin = msg.get("origin")
            self.coordinator = winner
            print(f"[{self.pid}] Received COORDINATOR announcement: {winner}")
            # forward unless we've completed a full circle
            if origin != self.pid:
                node, index = self._find_next_reachable(start_index=(self.idx + 1) % len(self.nodes_list))
                if node:
                    send_msg((node['host'], node['port']),
                             {"type":"COORDINATOR", "origin":origin, "coordinator":winner})
                    print(f"[{self.pid}] Forwarded COORDINATOR to {node['pid']}")
                else:
                    print(f"[{self.pid}] No reachable node to forward COORDINATOR")

        elif typ == "PING":
            send_msg((msg.get("from_host"), msg.get("from_port")), {"type":"PONG", "from":self.pid})

        elif typ == "PONG":
            pass

    def initiate_election(self):
        print(f"[{self.pid}] Initiating election...")
        # attempt to send ELECTION to first reachable node in ring order
        node, index = self._find_next_reachable(start_index=(self.idx + 1) % len(self.nodes_list))
        if node:
            send_msg((node['host'], node['port']),
                     {"type":"ELECTION", "origin":self.pid, "ids":[self.pid]})
            print(f"[{self.pid}] Sent ELECTION to {node['pid']}")
        else:
            # no other reachable node -> become coordinator
            with self.lock:
                self.coordinator = self.pid
            print(f"[{self.pid}] No reachable neighbors, becoming COORDINATOR")
            # try to announce to any reachable nodes (best-effort)
            for n in self.nodes_list:
                if n["pid"] == self.pid:
                    continue
                send_msg((n["host"], n["port"]),
                         {"type":"COORDINATOR", "origin":self.pid, "coordinator":self.pid})

    def heartbeat_loop(self):
        def loop():
            while self.alive:
                time.sleep(3)
                with self.lock:
                    coord = self.coordinator
                if coord is None or coord == self.pid:
                    continue
                addr = self.nodes_by_pid.get(coord)
                if not addr:
                    continue
                ok = send_msg(addr, {"type":"PING", "from":self.pid, "from_host":self.host, "from_port":self.port}, timeout=1)
                if not ok:
                    print(f"[{self.pid}] Coordinator {coord} not responding -> starting election")
                    self.initiate_election()
        threading.Thread(target=loop, daemon=True).start()

    def startup(self):
        time.sleep(1)
        print(f"[{self.pid}] Starting initial election")
        self.initiate_election()

    def stop(self):
        self.alive = False
        if self.server:
            try:
                self.server.close()
            except Exception:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    args = parser.parse_args()

    # locate nodes.json next to this script to avoid working-dir issues
    script_dir = os.path.dirname(os.path.abspath(__file__))
    nodes_path = os.path.join(script_dir, "nodes.json")

    if not os.path.exists(nodes_path):
        print(f"Error: nodes.json not found at {nodes_path}")
        sys.exit(1)

    try:
        with open(nodes_path, "r", encoding="utf-8") as f:
            nodes = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse nodes.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unable to open nodes.json: {e}")
        sys.exit(1)

    pids = [n["pid"] for n in nodes]
    if args.pid not in pids:
        print("PID not in nodes.json")
        sys.exit(1)

    node = RingNode(args.pid, nodes)
    try:
        node.start_server()
        node.heartbeat_loop()
        node.startup()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"[{node.pid}] Shutting down")
        node.stop()
        time.sleep(0.5)