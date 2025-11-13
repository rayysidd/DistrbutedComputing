# File: ring/node.py
"""
Ring-based token passing node.
Run N nodes on localhost using different ports.
Example (3 nodes, base-port 5000):
Terminal 1: python ring/node.py --id 0 --n 3 --base-port 5000 --initial-holder
Terminal 2: python ring/node.py --id 1 --n 3 --base-port 5000
Terminal 3: python ring/node.py --id 2 --n 3 --base-port 5000

This simple implementation uses TCP sockets. Each node runs a server that
receives messages and a client side that connects to the next node to pass the token.
"""

import argparse
import socket
import threading
import time
import random

BUFFER_SIZE = 1024

class RingNode:
    def __init__(self, node_id, n, base_port, initial_holder=False):
        self.id = node_id
        self.n = n
        self.base_port = base_port
        self.port = base_port + node_id
        self.next_port = base_port + ((node_id + 1) % n)
        self.has_token = initial_holder
        self.want_cs = False
        self.lock = threading.Lock()
        self.shutdown = False

    def start(self):
        server_thread = threading.Thread(target=self.server_loop, daemon=True)
        server_thread.start()

        # Start token loop in main thread
        try:
            self.run_loop()
        except KeyboardInterrupt:
            print("\nNode shutting down.")
            self.shutdown = True

    def server_loop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", self.port))
        s.listen()
        print(f"[Node {self.id}] Listening on port {self.port}. Next -> {self.next_port}")
        while not self.shutdown:
            try:
                conn, addr = s.accept()
                data = conn.recv(BUFFER_SIZE).decode()
                conn.close()
                if not data:
                    continue
                # handle incoming message
                if data.strip() == "TOKEN":
                    with self.lock:
                        self.has_token = True
                else:
                    print(f"[Node {self.id}] Unknown message: {data}")
            except OSError:
                break
            except Exception as e:
                print(f"[Node {self.id}] Server error: {e}")
                break
        s.close()

    def send_token(self):
        # connect to next and send TOKEN
        msg = "TOKEN"
        try:
            with socket.create_connection(("10.10.114.136", self.next_port), timeout=2) as sock:
                sock.sendall(msg.encode())
            print(f"[Node {self.id}] Passed token to node {(self.id+1)%self.n} (port {self.next_port})")
        except Exception as e:
            print(f"[Node {self.id}] Failed to pass token to port {self.next_port}: {e}")

    def run_loop(self):
        # separate thread to randomly decide wanting CS
        threading.Thread(target=self.random_want_cs, daemon=True).start()

        while not self.shutdown:
            # If we have token, decide to enter CS or pass immediately
            if self.has_token:
                print(f"[Node {self.id}] I have the token.")
                if self.want_cs:
                    print(f"[Node {self.id}] Entering Critical Section...")
                    # simulate critical section
                    time.sleep(2 + random.random())
                    print(f"[Node {self.id}] Leaving Critical Section.")
                    self.want_cs = False
                else:
                    print(f"[Node {self.id}] Not interested in CS right now.")

                # After finishing (or if not interested) pass the token
                self.has_token = False
                # small delay to simulate processing
                time.sleep(0.5)
                self.send_token()
            else:
                # Wait and check again
                time.sleep(0.5)

    def random_want_cs(self):
        # Randomly set want_cs to True every few seconds to simulate requests
        while not self.shutdown:
            # Decide every 4-8 seconds
            time.sleep(4 + random.random() * 4)
            # 50% chance to request
            if random.random() < 0.5:
                with self.lock:
                    self.want_cs = True
                print(f"[Node {self.id}] Requested to enter CS (will wait for token).")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=int, required=True, help='node id (0..n-1)')
    parser.add_argument('--n', type=int, required=True, help='number of nodes')
    parser.add_argument('--base-port', type=int, default=5000, help='base port for nodes')
    parser.add_argument('--initial-holder', action='store_true', help='start with token')
    args = parser.parse_args()

    node = RingNode(args.id, args.n, args.base_port, initial_holder=args.initial_holder)
    node.start()