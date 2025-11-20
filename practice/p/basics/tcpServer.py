import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5000))
server.listen()

print("Server running...")

while True:
    client, addr = server.accept()
    print("Connected:", addr)

    data = client.recv(1024).decode()
    print("From client:", data)

    client.send("Hello Client".encode())
    client.close()
