import socket
import sys

NUM_CLIENTS = 2
client_index = 0  # Assuming this client is at index 0
client_vector_clock = [0] * NUM_CLIENTS

def send_vector_clock(server_ip, server_port=6000):
    global client_vector_clock
    client_vector_clock[client_index] += 1  # Increment before sending
    print(f"Client vector clock on sending: {client_vector_clock}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        s.sendall(str(client_vector_clock).encode())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <Server_IP>")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    send_vector_clock(server_ip)