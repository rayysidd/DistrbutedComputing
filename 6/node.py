# node.py
import socket
import time
import random

HOST = '127.0.0.1'  # Leader IP
PORT = 5000

# Simulated local clock with slight random offset
local_clock = time.time() + random.uniform(-5, 5)  # ±5 seconds offset

print(f"[Client] Local clock before sync: {local_clock}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(str(local_clock).encode())  # Send local clock

    offset = float(s.recv(1024).decode())  # Receive offset from leader
    print(f"[Client] Offset received: {offset}")

    local_clock += offset  # Adjust local clock
    print(f"[Client] Local clock after sync: {local_clock}")
