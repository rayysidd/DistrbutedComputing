from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)
messages = [] # Store all messages from clients
# Route to view messages in browser
@app.route('/')
def index():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
    <title>Client Messages</title>
    <meta http-equiv="refresh" content="2">
    </head>
    <body>
    <h2>📨 Client Messages</h2>
    <ul>
    {% for msg in messages %}
    <li>{{ msg }}</li>
    {% endfor %}
    </ul>
    </body>
    </html>
    '''
    return render_template_string(html, messages=messages)
# API endpoint for client to send message
@app.route('/message', methods=['POST'])
def receive_message():
    data = request.get_json()
    msg = data.get('message', 'Empty')
    messages.append(msg)
    print("Received:", msg)
    return jsonify({"reply": "Message received!"})
# Run server
app.run(host='0.0.0.0', port=5007)