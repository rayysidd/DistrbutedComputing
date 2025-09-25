# server.py
import socket
import time

HOST = '127.0.0.1'  # localhost
PORT = 5000

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[Server] Listening on {HOST}:{PORT}...")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"[Server] Connection from {addr}")
            server_time = time.time()
            conn.sendall(str(server_time).encode())
            print(f"[Server] Sent time {server_time}")
