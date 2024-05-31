from datetime import datetime, timezone

def get_current_utc_time():
    # Format the time as a string in the MySQL TIMESTAMP format ('YYYY-MM-DD HH:MM:SS')
    formatted_utc_time = datetime.strptime(get_current_utc_time_string(), '%Y-%m-%d %H:%M:%S')
    
    return formatted_utc_time

def get_current_utc_time_string():
    # Get the current time in UTC
    current_utc_time = datetime.now(timezone.utc)
    
    # Format the time as a string in the MySQL TIMESTAMP format ('YYYY-MM-DD HH:MM:SS')
    formatted_utc_time = current_utc_time.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_utc_time

def convert_string_time_to_datetime(time_string):
    # Convert the string to a datetime object
    time_object = datetime.strptime(str(time_string), '%Y-%m-%d %H:%M:%S')
    
    return time_object