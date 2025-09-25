# leader.py
import socket
import time

HOST = '127.0.0.1'
PORT = 5000
NUM_NODES = 3  # Number of connected nodes

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[Server] Listening on {HOST}:{PORT}...")

    node_connections = []
    node_times = []

    # Accept connections from all nodes
    while len(node_connections) < NUM_NODES:
        conn, addr = s.accept()
        node_connections.append((conn, addr))
        node_time = float(conn.recv(1024).decode())
        node_times.append((addr, node_time))
        print(f"[Server] Received time {node_time} from {addr}")

    # Leader's own clock
    master_clock = time.time()
    print(f"[Server] Master clock time: {master_clock}")

    # Include master clock for averaging
    all_times = [master_clock] + [t[1] for t in node_times]
    average_time = sum(all_times) / len(all_times)
    print(f"[Server] Average time: {average_time}")

    # Compute offsets for nodes
    for (conn, addr), (_, node_time) in zip(node_connections, node_times):
        offset = average_time - node_time
        conn.sendall(str(offset).encode())
        print(f"[Server] Sent offset {offset:.6f} to {addr}")

    # Adjust master clock
    master_offset = average_time - master_clock
    master_clock += master_offset
    print(f"[Server] Adjusting master by {master_offset:.6f} seconds")
