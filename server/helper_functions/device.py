import hashlib
import random
from flask import jsonify
from helper_functions.database import execute_sql
from helper_functions.time_helper import get_current_utc_time_string
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
