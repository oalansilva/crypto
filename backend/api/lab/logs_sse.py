"""Compatibility shim.

The backend uses `app.routes.lab_logs_sse`; this module exists to match the
OpenSpec task path `backend/api/lab/logs_sse.py`.
"""

from app.routes.lab_logs_sse import *  # noqa: F401,F403

