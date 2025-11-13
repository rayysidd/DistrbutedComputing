import socket
import threading
import json

lock = False
waiting_clients = []

def handle_client(conn, addr):
    global lock, waiting_clients
    try:
        data = conn.recv(1024)
        if not data:
            conn.close()
            return

        msg = json.loads(data.decode())
        client_id = msg.get("id")
        msg_type = msg.get("type")

        if msg_type == "REQUEST":
            print(f"[Coordinator] REQUEST from {client_id}")
            if not lock:
                lock = True
                # Send GRANT immediately
                send_grant(client_id)
            else:
                # Add client to waiting list
                waiting_clients.append(client_id)
                print(f"[Coordinator] {client_id} added to waiting queue")

        elif msg_type == "RELEASE":
            print(f"[Coordinator] RELEASE from {client_id}")
            if waiting_clients:
                next_client = waiting_clients.pop(0)
                send_grant(next_client)
            else:
                lock = False

    except Exception as e:
        print(f"[Coordinator] Error: {e}")
    finally:
        conn.close()

def send_grant(client_id):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 6000 + int(client_id, 36)))  # Each client listens on 6000+id
        s.sendall(json.dumps({"type": "GRANT"}).encode())
        s.close()
        print(f"[Coordinator] GRANT sent to {client_id}")
    except Exception as e:
        print(f"[Coordinator] Failed to send GRANT to {client_id}: {e}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 6000))
    server.listen()
    print("[Coordinator] Running on port 6000")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
