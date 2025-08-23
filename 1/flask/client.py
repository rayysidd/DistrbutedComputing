import requests
import json 
server_ip = "10.10.119.64" #machine a ip
url = "http://10.10.119.64:5007/message"
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
        payload = {"message": message}
        response = requests.post(url, data=json.dumps(payload),
        headers=headers)
        print("Server: {}".format(response.text))
    except Exception as e:
        print("Error: {}".format(e))