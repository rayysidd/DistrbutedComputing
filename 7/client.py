import socket
import sys
import random
import time

# Initialize Lamport clock for client
client_clock = 0

def send_time(server_ip, server_port=5000):
    global client_clock
    client_clock += 1  # Increment Lamport clock before sending
    print(f"Client clock on sending: {client_clock}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        s.sendall(str(client_clock).encode())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <Server_IP>")
        sys.exit(1)

    server_ip = sys.argv[1]
    send_time(server_ip)
