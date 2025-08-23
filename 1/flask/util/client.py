import requests
import json 
import psutil
server_ip = "10.10.119.64" #machine a ip
url = "http://10.10.119.64:5007/message"

def system_summary():
    summary = ""
    summary += f"CPU Cores (logical): {psutil.cpu_count()}\n"
    summary += f"CPU Cores (physical): {psutil.cpu_count(logical=False)}\n"
    summary += f"Total CPU Usage: {psutil.cpu_percent(interval=1)}%\n"
    summary += f"Memory Usage: {psutil.virtual_memory().percent}%\n"
    summary += f"Disk Usage: {psutil.disk_usage('/').percent}%\n"
    summary += f"Battery Info: {psutil.sensors_battery()}" if hasattr(psutil, "sensors_battery") else "Battery Info: N/A"
    return summary

while True:
    try:
        message = input("You: ") # Use raw_input in Python 2.7
    except KeyboardInterrupt:
        print("\nExiting.")
        break
    if message.lower() == "exit":
        break
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {"message": system_summary()}
        response = requests.post(url, data=json.dumps(payload),
        headers=headers)
        print("Server: {}".format(response.text))
    except Exception as e:
        print("Error: {}".format(e))