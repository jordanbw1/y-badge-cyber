from flask import Flask, jsonify, request, render_template, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

credentials = {
    "identifier": "your_identifier",
    "password": "your_password"
}

global current_command, current_params
current_command = ""
current_params = ""

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/control_device', methods=['GET', 'POST'])
def control_device():
    if request.method == 'GET':
        return render_template('control_device.html')
    if request.method == 'POST':
        # Get the form data
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        color_hex = request.form.get('color')

        # Get IP address of the device
        device_ip = request.remote_addr

        # Convert the color value to R, G, B format
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)

        # Ensure RGB values are within the range of 0 to 255
        r = max(0, min(r, 255))
        g = max(0, min(g, 255))
        b = max(0, min(b, 255))

        global current_command, current_params
        current_command = 'change_led_color'
        current_params = {'r': r, 'g': g, 'b': b}

        # TODO: Save the command in DB for the given device
        return render_template('control_device.html')

@app.route('/get_credentials', methods=['GET'])
def get_credentials():
    return jsonify(credentials)

@app.route('/poll_commands', methods=['GET'])
def poll_commands():
    global current_command, current_params
    if current_command == 'change_led_color':
        commands = {'command': current_command, 'r': current_params["r"], 'g': current_params["g"], 'b': current_params["b"]}
        # TODO: Update last check in time with device in DB
        return jsonify(commands)
    return jsonify({'command': None})

@app.route('/confirm_command', methods=['GET'])
def confirm_command():
    global current_command, current_params
    # Get the command from the request
    command = request.args.get('data')

    # Get IP address of the device
    device_ip = request.remote_addr

    # TODO: Mark command as executed in DB for the given device

    current_command = ""
    current_params = ""

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
