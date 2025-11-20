from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/")
def home():
    return "Server is running"

@app.post("/echo")
def echo():
    data = request.get_json()
    return jsonify({"you_sent": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
