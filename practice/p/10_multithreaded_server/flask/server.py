from flask import Flask,request
import threading

app=Flask(__name__)

@app.route("/process",methods=['POST'])
def process():
    print("Handling client in thread: ",threading.get_ident)
    text = request.json.get("text", "")
    return {"response": "Processed: " + text}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)