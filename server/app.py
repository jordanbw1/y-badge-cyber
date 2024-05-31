from flask import Flask, jsonify, request, render_template, url_for
from dotenv import load_dotenv
import os
import datetime
import redis
import json
from helper_functions.device import insert_device_database, remove_device_database, update_last_seen, ensure_device_active
from helper_functions.time_helper import get_current_utc_time, convert_string_time_to_datetime

DEVICE_TIMEOUT_SECONDS = 300 # Time in seconds before a device is considered offline

load_dotenv(".env")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# Initialize Redis client
redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_client = redis.Redis(connection_pool=redis_pool)


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
    # Check if the IP address is in the DB
    device_ip = request.remote_addr
    redis_key = f"device:{device_ip}"
 
    device_data = redis_client.get(redis_key)
    
    if not device_data:
        # Insert device into Redis
        return insert_device_database(device_ip, redis_client)
    
    device_data = json.loads(device_data)
    last_seen = device_data.get('last_seen')
    if not last_seen:
        return insert_device_database(device_ip, redis_client)
    
    time_now = get_current_utc_time()
    last_seen = convert_string_time_to_datetime(str(last_seen))
    
    if (time_now - last_seen).total_seconds() > DEVICE_TIMEOUT_SECONDS:
        # Remove device from Redis
        status, message = remove_device_database(device_ip, redis_client)
        if not status:
            return jsonify({'error': message}), 400
        # Insert new device into Redis
        return insert_device_database(device_ip, redis_client)
    
    # Update the last seen time
    update_last_seen(device_ip, redis_client)
    return jsonify({'identifier': device_ip}), 200

@app.route('/poll_commands', methods=['GET'])
def poll_commands():
    # Get IP address of the device
    device_ip = request.remote_addr
    # Ensure that device is in the DB and update last seen time
    status, message = ensure_device_active(device_ip, DEVICE_TIMEOUT_SECONDS, redis_client)
    if not status:
        return jsonify({'error': message}), 400
    # TODO: Get the command from the DB
    # global current_command, current_params
    # if current_command == 'change_led_color':
    #     commands = {'command': current_command, 'r': current_params["r"], 'g': current_params["g"], 'b': current_params["b"]}
    #     # TODO: Update last check in time with device in DB
    #     return jsonify(commands)
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
