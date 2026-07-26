def parse_log_line(line: str) -> dict:
    if not isinstance(line, str):
        raise TypeError("Log line must be a string")
    
    parts = line.split("|")

    if len(parts) <4:
        raise ValueError("Invalid log format")
    
    timestamp = parts[0].strip()
    user_id = parts[1].strip()
    status_str = parts[2].strip()   
    response_str = parts[3].strip()

    try:
        status_code = int(status_str)
    except ValueError:
        raise ValueError("Status code must be numeric")
    
    try:
        response_time = float(response_str)
    except ValueError:
        raise ValueError("Response time must be numeric")
    
    if response_time < 0:
        raise ValueError("Response time cannot be negative")

    return{
        "timestamp": timestamp,
        "user_id": user_id,
        "status_code": status_code,
        "response_time": response_time    
    } 
