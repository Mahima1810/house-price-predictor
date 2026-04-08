"""Vercel/Flask entrypoint.

Vercel looks for a top-level Flask app in files like app.py.
We keep the actual implementation in backend/app.py.
"""

from backend.app import app  # noqa: F401
