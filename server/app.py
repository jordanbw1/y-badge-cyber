from flask import Flask, jsonify, request, render_template, url_for
from dotenv import load_dotenv
import os
import datetime
import hashlib
import re
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


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/control_device', methods=['GET', 'POST'])
def control_device():
    if request.method == 'GET':
        return render_template('control_device.html')
    if request.method == 'POST':
        # Get the form data
        device_ip = request.form.get('identifier')
        password = request.form.get('password')
        color_hex = request.form.get('color')

        # Ensure password matches hash in database
        redis_key = f"device:{device_ip}"
        device_data = redis_client.get(redis_key)
        if not device_data:
            return jsonify({'error': 'Device not found'}), 400
        
        device_data = json.loads(device_data)
        hashed_password = device_data.get('password')
        if not hashed_password:
            return jsonify({'error': 'Device not found'}), 400
        
        # Compare the password with the hash in the database
        hashed_input_password = hashlib.md5(password.encode()).hexdigest()
        if hashed_input_password != hashed_password:
            return jsonify({'error': 'Invalid password'}), 400


        # Ensure ip address is in IP format with regex
        ip_regex = re.compile(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$')
        if not ip_regex.match(device_ip):
            print("Invalid IP address format")
            return jsonify({'error': 'Invalid IP address format'}), 400        

        # Convert the color value to R, G, B format
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)

        # Ensure RGB values are within the range of 0 to 255
        r = max(0, min(r, 255))
        g = max(0, min(g, 255))
        b = max(0, min(b, 255))

        # Save the command in Redis for the given device
        command_data = {
            'command': 'change_led_color',
            'params': {'r': r, 'g': g, 'b': b}
        }
        redis_client.set(f"device_command:{device_ip}", json.dumps(command_data))

        return jsonify({'status': 'success'}), 200

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
    
    # Get the command from the DB
    command_data_json = redis_client.get(f"device_command:{device_ip}")
    print("command_data_json", command_data_json)
    if command_data_json:
        command_data = json.loads(command_data_json)
        commands = {'command': command_data["command"], 'r': command_data["params"]["r"], 'g': command_data["params"]["g"], 'b': command_data["params"]["b"]}
        return jsonify(commands)
    
    # Return None if no command is found
    return jsonify({'command': None})

@app.route('/confirm_command', methods=['GET'])
def confirm_command():
    # Get the command from the request
    command = request.args.get('data')

    # Get IP address of the device
    device_ip = request.remote_addr

    # Mark command as executed in DB for the given device
    redis_client.delete(f"device_command:{device_ip}")

    return jsonify({'status': 'success'})

@app.route('/admin', methods=['GET'])
def admin():
    # TODO: Implement vulnerable admin route
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
