import requests

url = "http://127.0.0.1:5000/echo"

payload = {
    "message": "Hello from client"
}

response = requests.post(url, json=payload)

print("Server responded:", response.json())
