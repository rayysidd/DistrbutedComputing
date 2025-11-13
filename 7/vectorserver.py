import socket

NUM_CLIENTS = 4  # Number of clients
VECTOR_SIZE = NUM_CLIENTS + 1  # Including server
server_vector_clock = [0] * VECTOR_SIZE
next_client_index = 1  # To assign indices dynamically

def update_vector_clock(received_vector, sender_index):
    global server_vector_clock
    # Element-wise max
    server_vector_clock = [
        max(server_vector_clock[i], received_vector[i]) for i in range(VECTOR_SIZE)
    ]
    # Increment server's own index
    server_vector_clock[0] += 1
    return server_vector_clock

def start_server(host="0.0.0.0", port=6000):
    global next_client_index
    print("Starting Vector Clock Server…")
    print(f"Server is listening on {host}:{port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                # Receive client's vector clock
                data = conn.recv(1024)
                if not data:
                    break

                # Decode client vector and index
                received = data.decode().strip().split(';')
                client_vector = list(map(int, received[0].strip('[]').split(',')))
                client_index = int(received[1])

                print(f"Connection from {addr} with client index {client_index}")
                print(f"Received client vector clock: {client_vector}")

                updated_vector = update_vector_clock(client_vector, client_index)
                print(f"Updated server vector clock: {updated_vector}")

if __name__ == "__main__":
    start_server()
