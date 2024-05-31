import hashlib
import random
from flask import jsonify
from helper_functions.database import execute_sql, sql_results_one
from helper_functions.time_helper import get_current_utc_time, get_current_utc_time_string
import os

def insert_device_database(device_ip):
    """
    Insert a new device into the database.
    Parameters:
    - device_ip: The IP address of the device.
    Returns:
    - status: True if the operation was successful, False otherwise.
    - message: A message indicating the result of the operation.
    """
    # Generate random insecure md5 password
    password = generate_md5_password()
    # Get the current time in UTC
    last_seen = get_current_utc_time_string()
    # Insert device and password into the DB
    query = "INSERT INTO devices (ip_address, password, last_seen) VALUES (%s, %s, %s)"
    values = (device_ip, password, last_seen)
    status, message = execute_sql(query, values)
    # If there was an error, return the error message
    if not status:
        return jsonify({'error': message}), 400
    # Return success message with device identifier
    return jsonify({'identifier': device_ip}), 200

def remove_device_database(device_ip):
    """
    Remove a device from the database.
    Parameters:
    - device_ip: The IP address of the device.
    Returns:
    - status: True if the operation was successful, False otherwise.
    - message: A message indicating the result of the operation.
    """
    query = "DELETE FROM devices WHERE ip_address = %s"
    values = (device_ip,)
    status, message = execute_sql(query, values)
    if not status:
        return status, message
    return status, "Good"

def update_last_seen(device_ip):
    """
    Update the last seen time for a device in the database.
    Parameters:
    - device_ip: The IP address of the device.
    Returns:
    - status: True if the operation was successful, False otherwise.
    - message: A message indicating the result of the operation.
    """
    time_now = get_current_utc_time_string()
    query = "UPDATE devices SET last_seen = %s WHERE ip_address = %s"
    values = (time_now, device_ip)
    status, message = execute_sql(query, values)
    if not status:
        return status, message
    return status, "Good"

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
    return hashed_password

def check_last_seen(device_ip, device_timeout_seconds):
    """
    Check if the last seen time for a device in the database is within specified interval.
    Parameters:
    - device_ip: The IP address of the device.
    Returns:
    - status: True if the operation was successful, False otherwise.
    - message: A message indicating the result of the operation.
    """
    query = "SELECT last_seen FROM devices WHERE ip_address = %s"
    values = (device_ip,)
    status, message, results = sql_results_one(query, values)
    if not status or not results:
        return False, "Device not found"
    last_seen = results[0]
    time_now = get_current_utc_time()
    if (time_now - last_seen).total_seconds() > device_timeout_seconds:
        return False, "Device has not been seen in the specified time interval"
    return True, "Device has been seen in the specified time interval"

def ensure_device_active(device_ip, device_timeout_seconds):
    """
    Check if a device is active, and update the last seen time if it is.
    Parameters:
    - device_ip: The IP address of the device.
    Returns:
    - status: True if the device is active, False otherwise.
    - message: A message indicating the result of the operation.
    """
    # Check the last seen time for the device
    status, message = check_last_seen(device_ip, device_timeout_seconds)

    # If device hasn't been seen, remove device from DB and insert new device
    if not status:
        # Remove device from DB
        status, message = remove_device_database(device_ip)
        if not status:
            return False, message
        # Insert device into DB
        return insert_device_database(device_ip)
    
    # Report that device is still active, and update last seen time
    status, message = update_last_seen(device_ip)
    if not status:
        return False, message
    return True, "Device is active"
