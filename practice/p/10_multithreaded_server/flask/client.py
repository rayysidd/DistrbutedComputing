import requests

while True:
    msg = input("Enter message (or exit): ")

    if msg.lower() == "exit":
        break

    res = requests.post(
        "http://127.0.0.1:12000/process",
        json={"text": msg}
    )

    print("Server:", res.json()["response"])