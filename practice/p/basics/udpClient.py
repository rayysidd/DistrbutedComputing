import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto("Ping".encode(), ("127.0.0.1", 6000))
print(sock.recvfrom(1024))
