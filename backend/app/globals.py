# file: backend/app/globals.py
# Global in-memory stores for ephemeral data like progress

# Progress Store
# Key: run_id (str), Value: {'progress': float (0-100), 'step': str}
RUN_PROGRESS = {}
