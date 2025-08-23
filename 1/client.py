import socket
import datetime
# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server
client_socket.connect(('localhost', 8002)) # Change if needed
print("Connected to server. Type messages below (type 'exit' to quit):")
while True:
    # Input from user (Python 2/3 compatible)
    message = input("You: ")
    # Add current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = "[{}] {}".format(timestamp, message)
    # Send the message with timestamp
    client_socket.send(full_message.encode())
    # Exit condition
    if message.lower() == 'exit':
        break
    # Receive and display server response
    response = client_socket.recv(1024).decode()
    print("Server:", response)
client_socket.close()
print("Disconnected from server.")