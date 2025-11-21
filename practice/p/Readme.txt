Project Title
Simple overview of use/purpose.

Description
An in-depth paragraph about your project and overview of use.

Getting Started
Dependencies
Describe any prerequisites, libraries, OS version, etc., needed before installing program.
ex. Windows 10
Installing
How/where to download your program
Any modifications needed to be made to files/folders
Executing program
How to run the program
Step-by-step bullets
code blocks for commands
Help
Any advise for common problems or issues.

command to run if program contains helper info
Authors
Contributors names and contact info

ex. Dominique Pizzie
ex. @DomPizzie

Version History
0.2
Various bug fixes and optimizations
See commit change or See release history
0.1
Initial Release
License
This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

Acknowledgments
Inspiration, code snippets, etc.

awesome-readme
PurpleBooth
dbader
zenorocha
fvcproductions



































































Q1 BANKING

"""
pip install flask requests

1. terminal 1 python server.py 1 5001
2. terminal 2 python server.py 2 5002
3. terminal 3 python server.py 3 5003

4. test system from any fresh terminal curl http://127.0.0.1:5001/status
5. perform transaction from any terminal (ubuntu specific)
curl -X POST http://127.0.0.1:5002/transfer \
     -H "Content-Type: application/json" \
     -d "{\"from\":\"Alice\",\"to\":\"Bob\",\"amount\":20}"

6. check balance curl http://127.0.0.1:5003/balance?acc=Alice

7. Test Leader Failure
Close (CTRL + C) the terminal running the leader
(leader = highest ID server).
Example:
Server 3 is leader → press CTRL+C in Terminal 3.
After 2–3 seconds, servers 1 and 2 will auto start election.
"""
"""
Distributed Banking System Simulation
- Bully leader election
- Leader acts as sequencer using Lamport logical clocks for global ordering
- REST APIs (Flask) for inter-server and client-server communication
- Heartbeat monitoring & leader re-election
"""

import sys
import threading
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --------------------------------------------------------------------------------
# CONFIG FROM COMMAND LINE
# --------------------------------------------------------------------------------
# python server.py <ID> <PORT>
my_id = int(sys.argv[1])
my_port = int(sys.argv[2])

# The cluster (modify ports as needed)
servers = {
    1: "http://127.0.0.1:5001",
    2: "http://127.0.0.1:5002",
    3: "http://127.0.0.1:5003"
}

# --------------------------------------------------------------------------------
# SHARED STATE
# --------------------------------------------------------------------------------
state = {
    "leader": None,
    "lamport": 0,
    "accounts": {"Alice": 100, "Bob": 100, "Mallory": 100}
}

# --------------------------------------------------------------------------------
# LAMPORT CLOCK UTILS
# --------------------------------------------------------------------------------
def tick():
    state["lamport"] += 1
    return state["lamport"]

def update_clock(received):
    state["lamport"] = max(state["lamport"], received) + 1
    return state["lamport"]

# --------------------------------------------------------------------------------
# LEADER ELECTION (BULLY ALGORITHM)
# --------------------------------------------------------------------------------
def start_election():
    print(f"[S{my_id}] Starting ELECTION...")
    higher = [sid for sid in servers if sid > my_id]

    got_ok = False
    for sid in higher:
        try:
            requests.get(servers[sid] + "/election")
            got_ok = True
        except:
            pass

    if not got_ok:
        # I AM LEADER
        state["leader"] = my_id
        print(f"[S{my_id}] I AM THE NEW LEADER.")
        announce_coordinator()

def announce_coordinator():
    for sid, url in servers.items():
        if sid != my_id:
            try:
                requests.post(url + "/coordinator", json={"leader": my_id})
            except:
                pass

@app.route("/election")
def election():
    # Responding "OK" to a lower ID server
    print(f"[S{my_id}] Got election request. Responding OK.")
    threading.Thread(target=start_election).start()
    return "OK"

@app.post("/coordinator")
def coordinator():
    leader = request.json["leader"]
    state["leader"] = leader
    print(f"[S{my_id}] New leader is S{leader}")
    return "ACK"

# --------------------------------------------------------------------------------
# HEARTBEAT MONITOR
# --------------------------------------------------------------------------------
def heartbeat_monitor():
    time.sleep(2)
    while True:
        time.sleep(2)
        if state["leader"] == my_id:
            continue

        leader_url = servers.get(state["leader"])
        try:
            requests.get(leader_url + "/heartbeat")
        except:
            print(f"[S{my_id}] Leader S{state['leader']} DOWN! Starting election...")
            start_election()

@app.get("/heartbeat")
def heartbeat():
    return "ALIVE"

# --------------------------------------------------------------------------------
# TRANSACTIONS
# --------------------------------------------------------------------------------
@app.post("/transfer")
def transfer():
    data = request.json
    frm = data["from"]
    to = data["to"]
    amt = data["amount"]

    tick()

    # If we are NOT leader → forward
    if state["leader"] != my_id:
        url = servers[state["leader"]] + "/transfer"
        return requests.post(url, json=data).text

    # LEADER HANDLES TRANSACTION
    seq = tick()
    print(f"[S{my_id}] Processing TX seq={seq}")

    # Apply transaction
    if state["accounts"][frm] >= amt:
        state["accounts"][frm] -= amt
        state["accounts"][to] += amt
    else:
        return jsonify({"status": "FAILED", "reason": "Insufficient funds"})

    # REPLICATE TO FOLLOWERS
    for sid, url in servers.items():
        if sid != my_id:
            try:
                requests.post(url + "/replicate",
                              json={"seq": seq, "from": frm, "to": to, "amount": amt,
                                    "clock": state["lamport"]})
            except:
                pass

    return jsonify({"status": "COMMITTED", "seq": seq})

# --------------------------------------------------------------------------------
# REPLICATION HANDLER
# --------------------------------------------------------------------------------
@app.post("/replicate")
def replicate():
    data = request.json
    seq = data["seq"]
    frm = data["from"]
    to = data["to"]
    amt = data["amount"]
    received_clock = data["clock"]

    update_clock(received_clock)
    print(f"[S{my_id}] Replicating TX seq={seq}")

    state["accounts"][frm] -= amt
    state["accounts"][to] += amt

    return "OK"

# --------------------------------------------------------------------------------
# UTILITY APIS
# --------------------------------------------------------------------------------
@app.get("/balance")
def balance():
    acc = request.args.get("acc")
    return jsonify({"account": acc, "balance": state["accounts"][acc]})

@app.get("/status")
def status():
    return jsonify({
        "server": my_id,
        "port": my_port,
        "leader": state["leader"],
        "lamport": state["lamport"],
        "accounts": state["accounts"]
    })

# --------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"[S{my_id}] Starting server on port {my_port}...")

    # Start heartbeat monitoring thread
    threading.Thread(target=heartbeat_monitor, daemon=True).start()

    # Delay first election so all servers start
    time.sleep(1)
    if state["leader"] is None:
        start_election()

    app.run(port=my_port, debug=False)















Q2 REMOTE CODE EXECUTION

SERVER
"""
1. teminal 1 rpc_server.py
2. terminal 2 rpc_client.py
"""
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import math


# Multi-threaded XMLRPC Server
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class RemoteExecutor:

    def execute_operation(self, op, data):
        """
        op = "eval"           → evaluate math expression
        op = "sort_list"      → sort python list
        op = "reverse_str"    → reverse string
        """

        try:
            if op == "eval":
                # Safe eval limited to math only
                allowed = {"__builtins__": None, "math": math}
                result = eval(data, allowed, {})
                return {"status": "ok", "result": result}

            elif op == "sort_list":
                return {"status": "ok", "result": sorted(data)}

            elif op == "reverse_str":
                return {"status": "ok", "result": data[::-1]}

            else:
                return {"status": "error", "result": "Unknown operation"}

        except Exception as e:
            return {"status": "error", "result": str(e)}


def main():
    server = ThreadedXMLRPCServer(("0.0.0.0", 8000), allow_none=True)
    server.register_instance(RemoteExecutor())

    print("RPC Server running on port 8000 (multithreaded)...")
    server.serve_forever()


if __name__ == "__main__":
    main()



CLIENT
import xmlrpc.client
import threading


SERVER_URL = "http://127.0.0.1:8000/"


def new_connection():
    return xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)


# --------------------
# Simple tests
# --------------------
def run_simple_tests():
    rpc = new_connection()

    print("Running simple tests...")
    print("Eval:", rpc.execute_operation("eval", "3*(2+5)"))
    print("Sort:", rpc.execute_operation("sort_list", [9, 1, 5, 2, 3]))
    print("Reverse:", rpc.execute_operation("reverse_str", "hello"))


# --------------------
# Threaded workers
# --------------------
def task_expr(i):
    rpc = new_connection()
    expr = f"({i} + {i}*2) / (1 + {i}%5 + 1)"
    try:
        print(f"Expr {i}:", rpc.execute_operation("eval", expr))
    except Exception as e:
        print(f"Expr error {i}:", e)


def task_sort(i):
    rpc = new_connection()
    arr = [i, i*3, i*2, i+1]
    try:
        print(f"Sort {i}:", rpc.execute_operation("sort_list", arr))
    except Exception as e:
        print(f"Sort error {i}:", e)


def task_reverse(i):
    rpc = new_connection()
    s = f"string_{i}"
    try:
        print(f"Reverse {i}:", rpc.execute_operation("reverse_str", s))
    except Exception as e:
        print(f"Reverse error {i}:", e)


# --------------------
# Multi-thread test
# --------------------
def run_concurrent_tests():
    print("\nRunning concurrent multi-thread tests...")

    threads = []
    for i in range(10):
        threads.append(threading.Thread(target=task_expr, args=(i,)))
        threads.append(threading.Thread(target=task_sort, args=(i,)))
        threads.append(threading.Thread(target=task_reverse, args=(i,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    run_simple_tests()
    run_concurrent_tests()




















Q3 Manage api keys 

"""
pip install flask

Ubuntu:
1.python3 api_key_server.py
---in another fresh terminal
2. Create one key   curl -X POST http://127.0.0.1:5000/create_key
3.Create multiple keys (5 keys)   curl -X POST http://127.0.0.1:5000/create_keys -H "Content-Type: application/json" -d '{"count":5}'
4.Get an available key   curl http://127.0.0.1:5000/get_key
5.Keep-alive a key   curl -X POST http://127.0.0.1:5000/keepalive -H "Content-Type: application/json" -d '{"key":"<uuid>"}'
6.Unblock a key  curl -X POST http://127.0.0.1:5000/unblock -H "Content-Type: application/json" -d '{"key":"<uuid>"}'
7. key status checking curl "http://127.0.0.1:5000/status?key=<uuid>"
8. dump all keys curl http://127.0.0.1:5000/dump


Windows:
1.Create one key   Invoke-RestMethod -Uri http://127.0.0.1:5000/create_key -Method POST
2.Create multiple keys (5 keys)   Invoke-RestMethod -Uri http://127.0.0.1:5000/create_keys -Method POST -Body '{"count":5}' -ContentType "application/json"
3.Get an available key   Invoke-RestMethod -Uri http://127.0.0.1:5000/get_key -Method GET
4.Keep-alive a key   Invoke-RestMethod -Uri http://127.0.0.1:5000/keepalive -Method POST -Body '{"key":"<uuid>"}' -ContentType "application/json"
5.Unblock a key   Invoke-RestMethod -Uri http://127.0.0.1:5000/unblock -Method POST -Body '{"key":"<uuid>"}' -ContentType "application/json"
6.key status checking   Invoke-RestMethod -Uri "http://127.0.0.1:5000/status?key=<uuid>" -Method GET
7.dump all keys   Invoke-RestMethod -Uri http://127.0.0.1:5000/dump -Method GET

"""
from 'create 1 key', we'll get
PS C:\Users\DELL> Invoke-RestMethod -Uri http://127.0.0.1:5000/create_key -Method POST

       created_at key                                  status
       ---------- ---                                  ------
1763396356.535721 210e9731-45d3-4dbe-a4d1-363d96d2f72a ok

in 'keep alive key', replace uuid with 210e9731-45d3-4dbe-a4d1-363d96d2f72a
Invoke-RestMethod -Uri http://127.0.0.1:5000/keepalive -Method POST -Body '{"key":"210e9731-45d3-4dbe-a4d1-363d96d2f72a"}' -ContentType "application/json"

key                                      last_keepalive status
---                                      -------------- ------
210e9731-45d3-4dbe-a4d1-363d96d2f72a 1763396616.7454185 ok
"""

import time
import uuid
import threading
from flask import Flask, request, jsonify, abort

# Configuration
KEY_TTL_SECONDS = 5 * 60      # 5 minutes lifetime unless keep-alive called
BLOCK_AUTO_RELEASE = 60       # 60 seconds auto-release for blocked keys
EXPIRY_SWEEP_INTERVAL = 10    # sweeper interval seconds
AUTO_RELEASE_INTERVAL = 5     # auto-unblock sweeper interval seconds

app = Flask(__name__)

# In-memory store
# key -> {
#   "key": str,
#   "status": "available" | "blocked",
#   "created_at": float(timestamp),
#   "last_keepalive": float(timestamp),
#   "blocked_at": float(timestamp) | None
# }
store = {}
store_lock = threading.Lock()


# ----- Helper utilities -----
def now_ts():
    return time.time()


def make_key():
    return str(uuid.uuid4())


def create_key_record():
    ts = now_ts()
    k = make_key()
    rec = {
        "key": k,
        "status": "available",
        "created_at": ts,
        "last_keepalive": ts,
        "blocked_at": None
    }
    return rec


# ----- Background sweepers -----
def expiry_sweeper():
    """Delete keys that have not been kept alive within TTL."""
    while True:
        time.sleep(EXPIRY_SWEEP_INTERVAL)
        with store_lock:
            to_delete = []
            for k, rec in store.items():
                if now_ts() - rec["last_keepalive"] > KEY_TTL_SECONDS:
                    to_delete.append(k)
            for k in to_delete:
                app.logger.info(f"Expiry sweeper deleting key {k} (no keepalive).")
                del store[k]


def auto_release_sweeper():
    """Auto-unblock keys that have been blocked longer than BLOCK_AUTO_RELEASE."""
    while True:
        time.sleep(AUTO_RELEASE_INTERVAL)
        with store_lock:
            for rec in store.values():
                if rec["status"] == "blocked" and rec["blocked_at"] is not None:
                    if now_ts() - rec["blocked_at"] > BLOCK_AUTO_RELEASE:
                        app.logger.info(f"Auto-release blocked key {rec['key']}")
                        rec["status"] = "available"
                        rec["blocked_at"] = None


# ----- Flask endpoints -----
@app.route("/create_key", methods=["POST"])
def create_key():
    rec = create_key_record()
    with store_lock:
        store[rec["key"]] = rec
    return jsonify({"status": "ok", "key": rec["key"], "created_at": rec["created_at"]})


@app.route("/create_keys", methods=["POST"])
def create_keys():
    data = request.json or {}
    count = int(data.get("count", 1))
    if count <= 0 or count > 1000:
        return jsonify({"status": "error", "error": "count must be between 1 and 1000"}), 400
    created = []
    with store_lock:
        for _ in range(count):
            rec = create_key_record()
            store[rec["key"]] = rec
            created.append(rec["key"])
    return jsonify({"status": "ok", "created": created})


@app.route("/get_key", methods=["GET"])
def get_key():
    """
    Provide an available key and mark it blocked so it won't be served again until unblocked or auto-released.
    """
    with store_lock:
        for rec in store.values():
            if rec["status"] == "available":
                rec["status"] = "blocked"
                rec["blocked_at"] = now_ts()
                return jsonify({
                    "status": "ok",
                    "key": rec["key"],
                    "blocked_at": rec["blocked_at"]
                })
    return jsonify({"status": "error", "error": "no available keys"}), 404


@app.route("/unblock", methods=["POST"])
def unblock_key():
    data = request.json or {}
    key = data.get("key")
    if not key:
        return jsonify({"status": "error", "error": "missing key"}), 400
    with store_lock:
        rec = store.get(key)
        if not rec:
            return jsonify({"status": "error", "error": "key not found"}), 404
        rec["status"] = "available"
        rec["blocked_at"] = None
    return jsonify({"status": "ok", "key": key})


@app.route("/keepalive", methods=["POST"])
def keepalive():
    data = request.json or {}
    key = data.get("key")
    if not key:
        return jsonify({"status": "error", "error": "missing key"}), 400
    with store_lock:
        rec = store.get(key)
        if not rec:
            return jsonify({"status": "error", "error": "key not found"}), 404
        rec["last_keepalive"] = now_ts()
    return jsonify({"status": "ok", "key": key, "last_keepalive": rec["last_keepalive"]})


@app.route("/status", methods=["GET"])
def status():
    key = request.args.get("key")
    if not key:
        return jsonify({"status": "error", "error": "missing key param"}), 400
    with store_lock:
        rec = store.get(key)
        if not rec:
            return jsonify({"status": "error", "error": "key not found"}), 404
        # do not return internal timestamps in production; ok for this experiment
        return jsonify({"status": "ok", "record": rec})


@app.route("/dump", methods=["GET"])
def dump_all():
    """Simple debug helper: list all keys (for testing only)."""
    with store_lock:
        return jsonify({"status": "ok", "keys": list(store.values())})


# ----- Main -----
if __name__ == "__main__":
    # Start background threads
    t1 = threading.Thread(target=expiry_sweeper, daemon=True)
    t2 = threading.Thread(target=auto_release_sweeper, daemon=True)
    t1.start()
    t2.start()

    # Run Flask
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)


















Q4 distributed logging sstem

log manager
import requests

# List of server ports
servers = [5001, 5002, 5003]  # add/remove servers as needed

all_logs = []

# Fetch logs from all servers
for port in servers:
    try:
        response = requests.get(f'http://127.0.0.1:{port}/get_logs')
        server_logs = response.json()
        all_logs.extend(server_logs)
    except Exception as e:
        print(f"Error connecting to server {port}: {e}")

# Sort logs by logical_clock, tie-break by server_id
all_logs_sorted = sorted(all_logs, key=lambda x: (x['logical_clock'], x['server_id']))

# Print logs
print("=== Centralized Logs (Globally Ordered) ===")
for log in all_logs_sorted:
    print(f"Server {log['server_id']} | LC: {log['logical_clock']} | Timestamp: {log['timestamp']} | Event: {log['event']}")






log server
"""
ubuntu:
1.terminal 1 python server.py 1 5001
2.terminal 2 python server.py 2 5002
3.terminal 3 python server.py 3 5003
3.terminal 4(Send log to Server 1) curl -X POST http://127.0.0.1:5001/generate_log -H "Content-Type: application/json" -d '{"event":"User login"}'
4.(Send log to Server 2) curl -X POST http://127.0.0.1:5002/generate_log -H "Content-Type: application/json" -d '{"event":"File uploaded"}'
5.python3 log_manager.py

Windows:
1.terminal 1 python server.py 1 5001
2.terminal 2 python server.py 2 5002
3.terminal 3 python server.py 3 5003
4.terminal 4(Send log to Server 1)Invoke-RestMethod -Uri http://127.0.0.1:5001/generate_log -Method POST -Body '{"event":"User login"}' -ContentType "application/json"
5.terminal 4(Send log to Server 2)Invoke-RestMethod -Uri http://127.0.0.1:5002/generate_log -Method POST -Body '{"event":"File uploaded"}' -ContentType "application/json"
6.terminal 4 python log_manager.py

"""
import time
from flask import Flask, request, jsonify

app = Flask(__name__)
logs = []
server_id = None
logical_clock = 0  # Lamport logical clock

@app.route('/generate_log', methods=['POST'])
def generate_log():
    global logical_clock
    event = request.json.get('event', 'No event')
    logical_clock += 1
    log = {
        'event': event,
        'server_id': server_id,
        'logical_clock': logical_clock,
        'timestamp': time.time()
    }
    logs.append(log)
    return jsonify({'status': 'ok', 'log': log})

@app.route('/get_logs', methods=['GET'])
def get_logs():
    return jsonify(logs)

def start_server(id, port):
    global server_id
    server_id = id
    app.run(host="127.0.0.1", port=port, threaded=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python server.py <server_id> <port>")
        sys.exit(1)
    server_id = int(sys.argv[1])
    port = int(sys.argv[2])
    start_server(server_id, port)











Q5 ARITHEMATIC SERVICE
 SERVER
"""
1.terminal 1 arith_server.py
2.terminal 2 arith_client.py
"""
from xmlrpc.server import SimpleXMLRPCServer
import threading

# Define arithmetic operations
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

# Start RPC server
def start_server(host="127.0.0.1", port=9000):
    server = SimpleXMLRPCServer((host, port), allow_none=True)
    print(f"Arithmetic RPC Server running on {host}:{port}")
    
    # Register functions
    server.register_function(add, 'add')
    server.register_function(subtract, 'subtract')
    server.register_function(multiply, 'multiply')
    server.register_function(divide, 'divide')
    
    server.serve_forever()

if __name__ == "__main__":
    start_server()


CLIENT
import xmlrpc.client

# Connect to the server
server = xmlrpc.client.ServerProxy("http://127.0.0.1:9000/")

print("Connected to Arithmetic RPC Server. Enter 'q' to quit.")

# Interactive mode only
while True:
    try:
        x_input = input("Enter first number (or 'q' to quit): ")
        if x_input.lower() == 'q':
            break
        x = float(x_input)
        y = float(input("Enter second number: "))

        print("Add:", server.add(x, y))
        print("Subtract:", server.subtract(x, y))
        print("Multiply:", server.multiply(x, y))
        print("Divide:", server.divide(x, y))
        print("-" * 40)

    except ValueError:
        print("Invalid input. Please enter numeric values.")
    except KeyboardInterrupt:
        print("\nExiting client.")
        break
    except Exception as e:
        print("Error:", e)



















Q6 VECTOR CLOCKS 

"""
### **Theory – Vector Clocks (Logical Clock Synchronization)**

1. **Objective:**

   * To synchronize events in a distributed system without relying on physical clocks.
   * Ensures **causal ordering** of events across multiple processes.

2. **Vector Clocks Concept:**

   * Each process maintains a **vector of counters**, one entry per process in the system.
   * Counters track the number of events **seen** by each process.

3. **Event Rules:**

   * **Internal event:** increment the counter of the process itself.
   * **Send event:** increment own counter, attach vector clock to message.
   * **Receive event:** element-wise maximum of local and received vector, then increment own counter.

4. **Causal Ordering:**

   * A vector clock allows comparison of events across processes:

     * If `V(A) < V(B)` → event A happened before event B (`A → B`)
     * If vectors are incomparable → events are **concurrent**.

5. **Use Cases:**

   * Detecting causality in distributed logs.
   * Ensuring consistent event ordering in distributed databases.
   * Conflict detection in replicated systems.

6. **Advantages:**

   * No reliance on synchronized physical clocks.
   * Provides **fine-grained causal relationships** between events.
   * Works for **any number of distributed processes**.

7. **Implementation:**

   * Each process updates its vector on **internal**, **send**, and **receive** events.
   * Events can be traced using **vector snapshots**, showing causal history.
"""
import threading
import time
import random

class Process:
    def __init__(self, pid, total_processes):
        self.pid = pid
        self.total = total_processes
        self.vector = [0] * total_processes
        self.events = []

    def internal_event(self):
        self.vector[self.pid] += 1
        self.events.append(('internal', list(self.vector)))
        print(f"Process {self.pid} internal event: {self.vector}")

    def send_event(self, target):
        self.vector[self.pid] += 1
        message = list(self.vector)
        self.events.append(('send', list(self.vector), target.pid))
        print(f"Process {self.pid} sent to {target.pid}: {message}")
        target.receive_event(message, self.pid)

    def receive_event(self, message, sender_id):
        self.vector = [max(self.vector[i], message[i]) for i in range(self.total)]
        self.vector[self.pid] += 1
        self.events.append(('receive', list(self.vector), sender_id))
        print(f"Process {self.pid} received from {sender_id}: {self.vector}")

# Simulation
def simulate():
    n = 3
    processes = [Process(i, n) for i in range(n)]

    # Threaded simulation of events
    def process_events(p):
        for _ in range(3):
            time.sleep(random.random())
            event_type = random.choice(['internal', 'send'])
            if event_type == 'internal':
                p.internal_event()
            else:
                target = random.choice([x for x in processes if x != p])
                p.send_event(target)

    threads = [threading.Thread(target=process_events, args=(p,)) for p in processes]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    simulate()













Q7 BULLY 
"""
### **Theory – Bully Algorithm for Leader Election**

1. **Objective:**

   * To elect a **coordinator** (leader) in a distributed system where nodes have **priorities (IDs)**.
   * Ensures the **highest-priority active node** becomes the leader.

2. **Node Priorities:**

   * Each node is assigned a **unique ID**; higher ID = higher priority.

3. **Election Process:**

   * When a node detects that the current leader has **failed**, it initiates an **election**.
   * The node sends **Election messages** to all nodes with **higher IDs**.
   * If no higher-ID node responds, the initiating node becomes the **leader** and sends **Coordinator messages** to all lower-ID nodes.
   * If a higher-ID node responds, that node **takes over the election**.

4. **Node Failure Handling:**

   * Nodes can be **inactive or crashed**, simulating failures.
   * The algorithm ensures **a new leader is elected** without conflict.

5. **Communication:**

   * Nodes exchange messages to announce **election initiation** and **coordinator declaration**.

6. **Use Case:**

   * Useful in distributed databases, server clusters, or networked systems where a **single coordinator** is needed.

7. **Advantages:**

   * Simple and deterministic.
   * Guarantees that the **highest-priority node** always becomes the leader.
   * Handles **simultaneous detection of failure** by multiple nodes.

8. **Output:**

   * Election steps show which nodes initiate, which respond, and the **final coordinator** known to each active node.

"""
import socket
import threading
import argparse
import json
import time

CONFIG_FILE = "nodes.json"

def load_nodes():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

class BullyNode:
    def __init__(self, pid):
        self.pid = pid
        self.nodes = load_nodes()
        self.host = None
        self.port = None
        self.coordinator = None

        for n in self.nodes:
            if n["pid"] == self.pid:
                self.host = n["host"]
                self.port = n["port"]

    def start(self):
        threading.Thread(target=self.listen_thread, daemon=True).start()
        time.sleep(1)
        print(f"[{self.pid}] Starting initial election")
        self.start_election()
        self.heartbeat_loop()

    def listen_thread(self):
        s = socket.socket()
        s.bind((self.host, self.port))
        s.listen()

        print(f"[{self.pid}] Listening on {self.host}:{self.port}")

        while True:
            conn, addr = s.accept()
            data = conn.recv(1024).decode()
            if not data:
                continue

            msg = json.loads(data)
            self.handle_message(msg)

    def send(self, pid, message):
        target = next((x for x in self.nodes if x["pid"] == pid), None)
        if not target:
            return

        try:
            s = socket.socket()
            s.connect((target["host"], target["port"]))
            s.send(json.dumps(message).encode())
            s.close()
        except:
            pass

    def handle_message(self, msg):
        if msg["type"] == "ELECTION":
            print(f"[{self.pid}] Received ELECTION from {msg['from']}")
            if self.pid > msg["from"]:
                self.send(msg["from"], {"type": "OK", "from": self.pid})
                self.start_election()

        elif msg["type"] == "OK":
            print(f"[{self.pid}] Received OK from {msg['from']}")
            self.ok_received = True

        elif msg["type"] == "COORDINATOR":
            print(f"[{self.pid}] New COORDINATOR = {msg['pid']}")
            self.coordinator = msg["pid"]

    def start_election(self):
        self.ok_received = False
        print(f"[{self.pid}] Initiating election...")

        for n in self.nodes:
            if n["pid"] > self.pid:
                self.send(n["pid"], {"type": "ELECTION", "from": self.pid})

        time.sleep(2)

        if not self.ok_received:
            print(f"[{self.pid}] I am the new COORDINATOR")
            self.coordinator = self.pid
            for n in self.nodes:
                if n["pid"] != self.pid:
                    self.send(n["pid"], {"type": "COORDINATOR", "pid": self.pid})
        else:
            print(f"[{self.pid}] Waiting for COORDINATOR announcement...")

    def heartbeat_loop(self):
        while True:
            time.sleep(3)
            if self.coordinator is None or self.coordinator == self.pid:
                continue

            if not self.check_alive(self.coordinator):
                print(f"[{self.pid}] Coordinator {self.coordinator} not responding → starting election")
                self.start_election()

    def check_alive(self, pid):
        try:
            s = socket.socket()
            target = next(x for x in self.nodes if x["pid"] == pid)
            s.settimeout(1)
            s.connect((target["host"], target["port"]))
            s.close()
            return True
        except:
            return False


# MAIN
parser = argparse.ArgumentParser()
parser.add_argument("--pid", type=int, required=True)
args = parser.parse_args()

node = BullyNode(args.pid)
node.start()







nodes.json
[
    { "pid": 1, "host": "127.0.0.1", "port": 5001 },
    { "pid": 2, "host": 127.0.0.1", "port": 5002 },
    { "pid": 3, "host": "127.0.0.1", "port": 5003 }
]






python3 bully_node.py --pid 1
python3 bully_node.py --pid 2
python3 bully_node.py --pid 3












Q8 RING 
"""
Theory – Ring Election Algorithm

Objective:

To elect a coordinator (leader) in a distributed system where processes are arranged in a logical ring.

Ensures only one leader is elected after a failure.

Ring Algorithm Concept:

Processes are connected in a unidirectional circular ring.

Each process knows only its successor.

If a process detects the leader has failed, it initiates an election:

It sends an Election message containing its ID around the ring.

Each process compares the ID in the message with its own ID:

If its own ID is higher, it replaces the ID in the message.

If lower, it passes the message unchanged.

When the message comes back to the initiator, the process with the highest ID becomes leader.

The new leader is then announced around the ring.

Node Failure Simulation:

Some processes can be marked inactive.

Election is triggered by an active process detecting failure.

Use Case:

Distributed databases or networked systems where a ring topology is preferred.

Advantages:

Simple, deterministic, and requires only local communication with the successor.

Works efficiently in ring topologies.
"""
import random

class Process:
    def __init__(self, pid):
        self.id = pid
        self.active = True
        self.leader = None
        self.successor = None

    def start_election(self):
        print(f"Process {self.id} starts election")
        election_message = [self.id]
        current = self.successor
        while True:
            if current.active:
                print(f"Message {election_message} passed to Process {current.id}")
                if current.id > election_message[0]:
                    election_message[0] = current.id
            current = current.successor
            if current == self:
                # Message completed one round
                self.leader = election_message[0]
                print(f"Election complete. New leader is Process {self.leader}")
                self.announce_leader()
                break

    def announce_leader(self):
        current = self.successor
        while current != self:
            if current.active:
                current.leader = self.leader
            current = current.successor

def simulate_ring():
    n = 5
    processes = [Process(i) for i in range(1, n+1)]
    # set successors in ring
    for i in range(n):
        processes[i].successor = processes[(i+1) % n]

    # Simulate leader failure
    leader = max(processes, key=lambda p: p.id)
    leader.active = False
    print(f"Process {leader.id} (current leader) is down!")

    # Start election from a random active process
    starter = random.choice([p for p in processes if p.active])
    starter.start_election()

    # Final leaders
    print("\nFinal leader known to each process:")
    for p in processes:
        status = "active" if p.active else "inactive"
        print(f"Process {p.id} ({status}) sees leader as {p.leader}")

if __name__ == "__main__":
    simulate_ring()














Q9 DISTRIBUTED KEY VALUE STORE 
"""
1. **Objective:**

   * Simulate a distributed key-value store across multiple replicas.
   * Demonstrate how updates propagate asynchronously, showing eventual consistency.

2. **Replica Nodes:**

   * Each node maintains its own copy of key-value pairs.
   * Nodes can process updates independently.

3. **Consistency Models:**

   * **Strong Consistency:** All replicas update immediately; all clients see the same value at all times.
   * **Eventual Consistency:** Updates propagate asynchronously; temporary inconsistencies are allowed, but all replicas **converge** eventually.

4. **Update Propagation:**

   * Changes made to one replica are propagated to other replicas after a simulated network delay.
   * Threading can be used to simulate asynchronous propagation.

5. **Observations:**

   * Immediately after an update, replicas may differ in value (demonstrating inconsistency).
   * After propagation, all replicas converge to the updated value (eventual consistency).

6. **Use Cases:**

   * Distributed caching systems, cloud databases, fault-tolerant storage solutions.
   * Prioritizes **availability and partition tolerance** over immediate consistency.

7. **Conclusion:**

   * Eventual consistency ensures system-wide convergence over time, making distributed systems resilient and scalable.

"""
import time
import threading

class Replica:
    def __init__(self, name):
        self.name = name
        self.store = {}
        self.lock = threading.Lock()

    def update(self, key, value):
        with self.lock:
            self.store[key] = value
            print(f"{self.name} updated {key} -> {value}")

    def get(self, key):
        with self.lock:
            return self.store.get(key, None)

def propagate_update(source, replicas, key, value, delay=2):
    """Propagate updates to other replicas after delay"""
    time.sleep(delay)
    for replica in replicas:
        if replica != source:
            replica.update(key, value)

# Simulation
def simulate_distributed_kv():
    # Create 3 replicas
    r1 = Replica("Replica1")
    r2 = Replica("Replica2")
    r3 = Replica("Replica3")
    replicas = [r1, r2, r3]

    # Initial values
    for r in replicas:
        r.update("x", 10)

    print("\n--- Eventual Consistency Demonstration ---")
    # Update r1
    r1.update("x", 50)
    threading.Thread(target=propagate_update, args=(r1, replicas, "x", 50, 3)).start()

    # Immediately check all replicas
    print(f"Immediate check: {[r.get('x') for r in replicas]}")

    # Wait for propagation
    time.sleep(4)
    print(f"After propagation: {[r.get('x') for r in replicas]}")

if __name__ == "__main__":
    simulate_distributed_kv()













Q10 MULTITHREADING

SERVER
import socket
import threading
import time

# Server Configuration
HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port to listen on

def handle_client(conn, addr):
    """
    Function to handle individual client requests.
    Run in a separate thread for each client.
    """
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        try:
            # Receive data from client (buffer size 1024 bytes)
            msg = conn.recv(1024).decode('utf-8')
            
            if not msg:
                break

            print(f"[{addr}] sent: {msg}")

            # --- Text Processing Logic ---
            # We convert text to Uppercase
            response = msg.upper()

            # --- Simulation of "Work" ---
            # We sleep for 5 seconds to prove that this thread doesn't block 
            # other clients from connecting at the same time.
            time.sleep(5) 

            # Send response back to client
            conn.send(response.encode('utf-8'))
            connected = False # Close connection after one request (for simplicity)

        except ConnectionResetError:
            break

    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    """
    Main server loop. Listens for connections and spawns threads.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        # Accept new connection
        conn, addr = server.accept()
        
        # Create a new thread for this specific client
        # target=handle_client tells the thread what function to run
        # args=(conn, addr) passes the arguments to that function
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        
        # Start the thread
        thread.start()
        
        # Print total active threads (subtract 1 for the main listener thread)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start_server()



CLIENT 

import socket
import time

HOST = '127.0.0.1'
PORT = 65432

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((HOST, PORT))
        
        # Get input from user
        message = input("Enter text to process (e.g., 'hello world'): ")
        
        print("Sending request...")
        client.send(message.encode('utf-8'))

        print("Waiting for response (Server sleeps for 5s to simulate work)...")
        
        # Receive response
        response = client.recv(1024).decode('utf-8')
        print(f"Server Response: {response}")

    except ConnectionRefusedError:
        print("Error: Could not connect to server. Is it running?")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()
















Q11 LOAD ABLANCER 

"""
Theory – Load Balancer Simulation

Objective:

A load balancer distributes incoming client requests to multiple backend servers.

Ensures no single server is overloaded and improves system responsiveness.

Backend Servers:

Simulated as threads or independent functions.

Each backend server processes requests concurrently.

Load Balancing Algorithms:

Round Robin: Requests are assigned sequentially to each server in turn.

Least Connections: Requests are sent to the server with the fewest active connections (optional).

Concurrency:

Multithreading allows multiple requests to be handled simultaneously.

Prevents blocking and improves throughput.

Request Handling:

Each request is processed independently.

Server maintains a count of requests handled to track load.

Output / Observation:

Requests are distributed among servers evenly (Round Robin).

Load distribution can be printed to verify balanced assignment.

Use Case:

Web servers, API gateways, distributed systems, and cloud services rely on load balancing for scalability and reliability.
"""

import threading
import time
import queue

class BackendServer:
    def __init__(self, name):
        self.name = name
        self.lock = threading.Lock()
        self.request_count = 0

    def handle_request(self, request_id):
        with self.lock:
            self.request_count += 1
            print(f"Server {self.name} handling request {request_id}. Total requests: {self.request_count}")
        # Simulate processing time
        time.sleep(1)

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.index = 0
        self.lock = threading.Lock()

    def route_request(self, request_id):
        with self.lock:
            server = self.servers[self.index]
            self.index = (self.index + 1) % len(self.servers)
        threading.Thread(target=server.handle_request, args=(request_id,)).start()

# Simulate
servers = [BackendServer("A"), BackendServer("B"), BackendServer("C")]
lb = LoadBalancer(servers)

# Simulate 10 incoming requests
for i in range(10):
    lb.route_request(i)
    time.sleep(0.2)
