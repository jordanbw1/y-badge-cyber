from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

credentials = {
    "identifier": "your_identifier",
    "password": "your_password"
}

@app.route('/get_credentials', methods=['GET'])
def get_credentials():
    return jsonify(credentials)

@app.route('/poll_commands', methods=['GET'])
def poll_commands():
    commands = {'command': 'change_led_color', 'r': 255, 'g': 0, 'b': 0}
    return jsonify(commands)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
