# -----------------------------------------------------------------------------
# File: boolean_lock/client.py
"""
Simple client that requests the centralized boolean lock, waits for GRANT, enters
critical section (simulated by sleep), then RELEASEs the lock. Keep the socket
open while waiting for GRANT.

Run:
python boolean_lock/client.py --id A --coordinator-port 6000
"""

import socket
import argparse
import time

BUFFER_SIZE = 1024

class LockClient:
    def __init__(self, client_id, coord_port):
        self.client_id = client_id
        self.coord_port = coord_port

    def request_and_use_lock(self): 
        try:
            with socket.create_connection(("10.10.113.58", self.coord_port), timeout=5) as sock:
                # Send REQUEST
                sock.sendall(f"REQUEST {self.client_id}\n".encode())
                print(f"Client {self.client_id}: REQUEST sent")

                # Wait for GRANT (blocking)
                while True:
                    data = sock.recv(BUFFER_SIZE).decode().strip()
                    if not data:
                        print(f"Client {self.client_id}: Connection closed by coordinator")
                        break
                    parts = data.split()
                    if parts[0].upper() == 'GRANT' and (len(parts) == 1 or parts[1] == self.client_id):
                        print(f"Client {self.client_id}: Received GRANT, entering CS...")
                        # simulate critical section
                        time.sleep(2)
                        print(f"Client {self.client_id}: Leaving CS, sending RELEASE")
                        sock.sendall(f"RELEASE {self.client_id}\n".encode())
                        # Optionally, request again or exit
                        break
                    else:
                        print(f"Client {self.client_id}: Unknown coordinator message: {data}")
        except Exception as e:
            print(f"Client {self.client_id}: Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True, help='client identifier (e.g., A)')
    parser.add_argument('--coordinator-port', type=int, default=6000, help='coordinator port')
    args = parser.parse_args()

    client = LockClient(args.id, args.coordinator_port)
    # For demo, loop a few times
    for i in range(3):
        client.request_and_use_lock()
        time.sleep(1 + i * 0.5)