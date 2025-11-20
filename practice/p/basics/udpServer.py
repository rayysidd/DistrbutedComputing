import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 6000))

while True:
    data, addr = sock.recvfrom(1024)
    print("From:", addr, "Data:", data.decode())
    sock.sendto("ACK".encode(), addr)
