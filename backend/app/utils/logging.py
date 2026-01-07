import os
import sys

def log_debug(message: str):
    """
    Helper to log to file and console simultaneously.
    Writes to backend/full_execution_log.txt
    """
    print(message)
    try:
        # Determine path to backend/full_execution_log.txt
        # We assume this file is in app/utils/logging.py
        # root is ../../
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_path = os.path.join(base_dir, "full_execution_log.txt")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f" Failed to write to log file: {e}")
