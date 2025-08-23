import socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8000))
server_socket.listen()
print("Server is listening on localhost:8000...")
conn, addr = server_socket.accept()
print("Connected by {}".format(addr))
while True:
    data = conn.recv(1024).decode()
    if not data or data.lower() == "exit":
        break
    print("Received: {}".format(data))
    conn.send("Echo: {}".format(data).encode())
conn.close()
print("Connection closed.")