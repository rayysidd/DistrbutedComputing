# client.py
import socket
import time

HOST = '127.0.0.1'  # Server IP
PORT = 5000

# Connect to the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    t0 = time.time()
    s.connect((HOST, PORT))
    s.sendall(b'Time request')
    
    server_time = float(s.recv(1024).decode())
    t1 = time.time()

# Round Trip Time
rtt = t1 - t0
one_way_delay = rtt / 2

# Adjusted time using Cristian's Algorithm
adjusted_time = server_time + one_way_delay

# Print results
print(f"[Client] Sent request at t0 = {t0}")
print(f"[Client] Received server time = {server_time} at t1 = {t1}")
print(f"[Client] RTT = {rtt:.6f} seconds")
print(f"[Client] Estimated one-way delay = {one_way_delay:.6f} seconds")
print(f"[Client] Adjusted time should be: {adjusted_time}")
