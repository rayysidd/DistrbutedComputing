import socket
import json
import time
import psutil
import platform
from datetime import datetime

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

def get_system_info():
    info = {
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'platform': platform.platform(),
        'hostname': platform.node()
    }
    return info

def main():
    while True:
        try:
            data = get_system_info()
            s = socket.socket()
            s.connect((SERVER_HOST, SERVER_PORT))
            s.send(json.dumps(data).encode())
            s.close()
            time.sleep(5)  # send every 5 seconds
        except Exception as e:
            print("Connection error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
