import hashlib
import random
from flask import jsonify
from helper_functions.time_helper import get_current_utc_time, get_current_utc_time_string, convert_string_time_to_datetime
import os
import json

def insert_device_database(device_ip, redis_client):
    """
    Insert a new device into the database.
    Parameters:
    - device_ip: The IP address of the device.
    - redis_client: The Redis client object.
    Returns:
    - status: True if the operation was successful, False otherwise.
    - message: A message indicating the result of the operation.
    """
    try:
        # Generate random insecure md5 password
        hashed_password, raw_password = generate_md5_password()
        # Get the current time in UTC
        last_seen = get_current_utc_time_string()
        # Insert device and password into Redis
        device_data = {'password': hashed_password, 'raw_password': raw_password, 'last_seen': last_seen}
        redis_key = f"device:{device_ip}"
        redis_client.set(redis_key, json.dumps(device_data))
        return jsonify({'ip_address': device_ip, 'password': raw_password}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def remove_device_database(device_ip, redis_client):
    """
    Remove a device from the database.
    Parameters:
    - device_ip: The IP address of the device.
    - redis_client: The Redis client object.
    Returns:
    - status: True if the operation was successful, False otherwise.
    - message: A message indicating the result of the operation.
    """
    try:
        redis_key = f"device:{device_ip}"
        if redis_client.exists(redis_key):
            redis_client.delete(redis_key)
            return True, "Good"
        else:
            return False, "Device not found"
    except Exception as e:
        return False, str(e)

def update_last_seen(device_ip, redis_client, last_hacked=False):
    """
    Update the last seen time for a device in the database.
    Parameters:
    - device_ip: The IP address of the device.
    - redis_client: The Redis client object.
    Returns:
    - status: True if the operation was successful, False otherwise.
    - message: A message indicating the result of the operation.
    """
    try:
        time_now = get_current_utc_time_string()
        redis_key = f"device:{device_ip}"
        if redis_client.exists(redis_key):
            device_data = json.loads(redis_client.get(redis_key))
            device_data['last_seen'] = time_now
            if last_hacked:
                device_data['last_hacked_time'] = time_now
            redis_client.set(redis_key, json.dumps(device_data))
            return True, "Good"
        else:
            return False, "Device not found"
    except Exception as e:
        return False, str(e)

def generate_md5_password():
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
    file_path = os.path.join(static_folder, "common_passwords.txt")
    # Read passwords from the file
    with open(file_path, 'r') as file:
        passwords = file.readlines()
    # Select a random password
    random_password = random.choice(passwords).strip()
    # Hash the password using MD5
    hashed_password = hashlib.md5(random_password.encode()).hexdigest()
    return hashed_password, random_password

def check_last_seen(device_ip, device_timeout_seconds, redis_client):
    """
    Check if the last seen time for a device in the database is within specified interval.
    Parameters:
    - device_ip: The IP address of the device.
    - device_timeout_seconds: The time interval in seconds within which the device must be seen.
    - redis_client: The Redis client object.
    Returns:
    - status: True if the operation was successful, False otherwise.
    - message: A message indicating the result of the operation.
    """
    try:
        redis_key = f"device:{device_ip}"
        if not redis_client.exists(redis_key):
            return False, "Device not found"
        device_data = json.loads(redis_client.get(redis_key))
        last_seen = device_data.get('last_seen')
        if not last_seen:
            return False, "Last seen time not found for device"
        time_now = get_current_utc_time()
        last_seen = convert_string_time_to_datetime(str(last_seen))
        if (time_now - last_seen).total_seconds() > device_timeout_seconds:
            return False, "Device has not been seen in the specified time interval"
        else:
            return True, "Device has been seen in the specified time interval"
    except Exception as e:
        return False, str(e)

def ensure_device_active(device_ip, device_timeout_seconds, redis_client):
    """
    Check if a device is active, and update the last seen time if it is.
    Parameters:
    - device_ip: The IP address of the device.
    - device_timeout_seconds: The time interval in seconds within which the device must be seen.
    - redis_client: The Redis client object.
    Returns:
    - status: True if the device is active, False otherwise.
    - message: A message indicating the result of the operation.
    """
    # Check the last seen time for the device
    status, message = check_last_seen(device_ip, device_timeout_seconds, redis_client)

    # If device hasn't been seen, remove device from DB and insert new device
    if not status:
        # Remove device from DB
        status, message = remove_device_database(device_ip, redis_client)
        if not status:
            return False, message, None
        # Insert device into DB
        result = insert_device_database(device_ip, redis_client)
        return True, "Successfully reinserted device", result
    
    # Report that device is still active, and update last seen time
    status, message = update_last_seen(device_ip, redis_client)
    if not status:
        return False, message, None
    return True, "Device is active", None

def update_password(device_ip, new_password, redis_client):
    """
    Updates the password for a device in the database.
    Parameters:
    - device_ip: The IP address of the device.
    - new_password: The new password for the device.
    - redis_client: The Redis client object.
    Returns:
    - status: True if the operation was successful, False otherwise.
    - message: A message indicating the result of the operation.
    """
    try:
        redis_key = f"device:{device_ip}"
        if not redis_client.exists(redis_key):
            return False, "Device not found", None

        # Load device data from Redis
        device_data = json.loads(redis_client.get(redis_key))
        
        # Generate random insecure md5 password
        hashed_password = hashlib.md5(new_password.encode()).hexdigest()

        # Update device data values
        device_data['last_seen'] = get_current_utc_time_string()
        device_data['password'] = hashed_password
        device_data['raw_password'] = new_password

        # Set values in Redis
        redis_client.set(redis_key, json.dumps(device_data))

        return True, "Successfully updated password", hashed_password
    
    except Exception as e:
        return False, "Error updating password: " + str(e), None