from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Serve your index.html file here
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# Endpoint to receive data from ESP32 for a button
@app.route('/button', methods=['POST'])
def button():
    print("Request body:", request.form)
    if request.is_json:
        data = request.json.get('data', '')
        print('Button data received:', data)
        socketio.emit('updateButtonData', data)  # Emit button data to all connected clients
        return 'Button Data Received', 200
    else:
        return 'Unsupported Media Type', 415

# Endpoint to receive data from ESP32 for a switch
@app.route('/switch', methods=['POST'])
def switch():
    print("Request body:", request.data)
    if request.is_json:
        data = request.json.get('data', '')
        print('Switch data received:', data)
        socketio.emit('updateSwitchData', data)  # Emit switch data to all connected clients
        return 'Switch Data Received', 200
    else:
        return 'Unsupported Media Type', 415

# Endpoint to receive data from ESP32 for a knob
@app.route('/knob', methods=['POST'])
def knob():
    print("Request body:", request.data)
    if request.is_json:
        data = request.json.get('data', '')
        print('Knob data received:', data)
        socketio.emit('updateKnobData', data)  # Emit knob data to all connected clients
        return 'Knob Data Received', 200
    else:
        return 'Unsupported Media Type', 415

@socketio.on('connect')
def handle_connect():
    print('A user connected')

if __name__ == '__main__':
    port = 5000
    socketio.run(app, host='0.0.0.0', port=port)
    print(f'Server running on http://localhost:{port}')
