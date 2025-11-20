import socket
import json

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000
FILE_NAME = 'client_info.txt'

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        conn, addr = s.accept()
        data = conn.recv(4096).decode()
        if data:
            info = json.loads(data)
            print(f"Received from {addr}: {info}")
            # Save to txt file
            with open(FILE_NAME, 'a') as f:
                f.write(f"{addr} -> {info}\n")
        conn.close()

if __name__ == "__main__":
    main()
