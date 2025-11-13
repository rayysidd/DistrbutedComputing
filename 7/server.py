import socket

# Initialize Lamport clock for server
server_clock = 0

def update_lamport_clock(received_time):
    global server_clock
    server_clock = max(server_clock, received_time) + 1
    return server_clock

def start_server(host="0.0.0.0", port=5000):
    global server_clock
    print("Starting Lamport Clock Server…")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Server is listening …….")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024)
                if not data:
                    break
                client_time = int(data.decode())
                print(f"Received client time: {client_time}")

                updated_time = update_lamport_clock(client_time)
                print(f"Updated server clock: {updated_time}")

if __name__ == "__main__":
    start_server()
