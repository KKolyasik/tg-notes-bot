import os


BACKEND_URL = os.getenv("BACKEND_URL", "http://bot:8080").rstrip("/")
API_KEY = os.getenv("BACKEND_API_KEY", "super-secret")
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "30"))
