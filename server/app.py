from flask import Flask, jsonify, request, render_template, url_for, session, redirect, flash, send_from_directory
from dotenv import load_dotenv
import os
import datetime
import hashlib
import re
import redis
import json
from helper_functions.device import insert_device_database, remove_device_database, update_last_seen, ensure_device_active, check_last_seen, update_password
from helper_functions.time_helper import get_current_utc_time, convert_string_time_to_datetime
from werkzeug.middleware.proxy_fix import ProxyFix # NOTE: Comment out for local testing


DEVICE_TIMEOUT_SECONDS = 300 # Time in seconds before a device is considered offline

load_dotenv(".env")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1) # NOTE: Comment out for local testing

# Initialize Redis client
redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis_client = redis.Redis(connection_pool=redis_pool)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/get_commands', methods=['GET'])
def get_commands():
    """
    Get the commands that the device can execute.
    Returns:
        JSON: JSON object containing the commands that the device can execute.
    
    """
    commands = {
        'endpoint': '/control_device',
        'method': 'POST',
        'parameters': [
            {
                'name': 'control_type',
                'type': 'str',
                'description': 'Type of control command to execute'
            },
            {
                'name': 'ip_address',
                'type': 'str',
                'description': 'IP address of the device'
            },
            {
                'name': 'password',
                'type': 'str',
                'description': 'Password of the device'
            }
        ],
        'description': 'These are the commands that the device can execute. Execute commands by sending a POST request to /control_device with the appropriate parameters. The device IP address and password are required to authenticate the device. The control_type parameter specifies the type of command to execute. The parameters for each command are specified in the commands list.',
        'commands': [
            {
                'command': 'change_led_color',
                'description': 'Change the color of the LED on the device',
                'parameters': [
                    {
                        'name': 'r',
                        'type': 'int',
                        'description': 'Red value of the LED color (0-255)'
                    },
                    {
                        'name': 'g',
                        'type': 'int',
                        'description': 'Green value of the LED color (0-255)'
                    },
                    {
                        'name': 'b',
                        'type': 'int',
                        'description': 'Blue value of the LED color (0-255)'
                    }
                ]
            },
            {
                'command': 'change_password',
                'description': 'Change the password of the device',
                'parameters': [
                    {
                        'name': 'new_password',
                        'type': 'str',
                        'description': 'New password for the device'
                    }
                ]
            },
            {
                'command': 'display_password',
                'description': 'Display the password of the device on the screen',
                'parameters': 'None'
            },
            {
                'command': 'hide_password',
                'description': 'Hide thepassword of the device from the screen',
                'parameters': 'None'
            }
        ]
    }
    return jsonify(commands)

@app.route('/control_device', methods=['GET', 'POST'])
def control_device():
    if request.method == 'GET':
        return render_template('control_device.html')
    if request.method == 'POST':
        # Get the form data
        device_ip = request.form.get('ip_address')
        password = request.form.get('password')
        control_type = request.form.get('control_type')

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

        # Check control type and execute the command
        if control_type == 'change_led_color':
            color_hex = request.form.get('color')
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
        elif control_type == 'change_password':
            new_password = request.form.get('new_password')
            # Hash the new password
            status, message, hashed_new_password = update_password(device_ip, new_password, redis_client)
            if not status:
                return jsonify({'error': message}), 400
            
            # Save the command in Redis for the given device
            command_data = {
                'command': 'change_password',
                'params': {'new_password': new_password}
            }
        elif control_type == 'display_password':
            # Save the command in Redis for the given device
            command_data = {
                'command': 'display_password',
                'params': {}
            }
        elif control_type == 'hide_password':
            # Save the command in Redis for the given device
            command_data = {
                'command': 'hide_password',
                'params': {}
            }
        else:
            return jsonify({'error': 'Invalid control type'}), 400
        
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

    # Get the password from the database
    device_data = redis_client.get(redis_key)
    device_data = json.loads(device_data)
    password = device_data.get('raw_password')
    if not password:
        return jsonify({'error': 'Device not found'}), 400
    return jsonify({'ip_address': device_ip, 'password': password}), 200

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
    # Return None if no command is found
    if not command_data_json:
        return jsonify({'command': None})
    
    command_data = json.loads(command_data_json)
    commands = {'command': None} # Set default command to None
    
    if command_data["command"] == 'change_led_color':
        commands = {'command': command_data["command"], 'r': command_data["params"]["r"], 'g': command_data["params"]["g"], 'b': command_data["params"]["b"]}
    elif command_data["command"] == 'change_password':
        commands = {'command': command_data["command"], 'new_password': command_data["params"]["new_password"]}
    elif command_data["command"] == 'rickroll':
        pass
    elif command_data["command"] == 'display_password':
        commands = {'command': command_data["command"]}
    elif command_data["command"] == 'hide_password':
        commands = {'command': command_data["command"]}
    else:
        return jsonify({'error': 'Invalid command'}), 400

    # TODO: Leave easter egg for playing rickroll or something. It would be a new command like 'rickroll'

    return jsonify(commands)
    

@app.route('/confirm_command', methods=['GET'])
def confirm_command():
    # Get the command from the request
    command = request.args.get('data')

    # Get IP address of the device
    device_ip = request.remote_addr

    # Mark command as executed in DB for the given device
    redis_client.delete(f"device_command:{device_ip}")

    return jsonify({'status': 'success'})

@app.route('/list_view', methods=['GET'])
def list_view():
    # Collect all endpoints
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':  # Exclude static files
            endpoints.append({
                'endpoint': rule.endpoint,
                'methods': ','.join(rule.methods),
                'path': str(rule)
            })
    return jsonify({'endpoints': endpoints})

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        # Get the form data
        ip_address = request.form.get('ip_address')
        # Confirm that the IP address is in the database and that it is active
        redis_key = f"device:{ip_address}"
        device_data = redis_client.get(redis_key)
        if not device_data:
            flash("Device not found")
            return render_template('admin_login.html')
        
        # Confirm device is active
        status, message = check_last_seen(ip_address, DEVICE_TIMEOUT_SECONDS, redis_client)
        if not status:
            flash("Error occured: " + message)
            return render_template('admin_login.html')

        # Get the device data
        device_data = json.loads(device_data)
        session['admin'] = True
        session['device_ip'] = ip_address
        
        return redirect(url_for('admin'))

@app.route('/admin_logout', methods=['GET'])
def admin_logout():
    # Clear the session
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin', methods=['GET'])
def admin():
    # Check if the user is an admin
    if 'admin' not in session or session['admin'] != True:
        flash("Hah! You though we were that dumb? No you have to sign in first!")
        return redirect(url_for('admin_login'))
    
    # Query database for password for the device
    device_ip = session['device_ip']
    redis_key = f"device:{device_ip}"
    device_data = redis_client.get(redis_key)
    if not device_data:
        flash("Device not found")
        return redirect(url_for('index'))
    
    # Get the device data
    device_data = json.loads(device_data)
    password = device_data.get('password')
    if not password:
        flash("Device not found")
        return redirect(url_for('index'))
    
    # Render page that shows the info they want.
    return render_template('admin.html', device_ip=device_ip, password=password)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/robots.txt', methods=['GET'])
def robots():
    return send_from_directory(app.static_folder, "robots.txt")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
