# === File: run.py ===
# Entry point to run the app using either Uvicorn (ASGI) or Flask directly (WSGI)

from app.main import app
from asgiref.wsgi import WsgiToAsgi

# Wrap Flask with ASGI compatibility for Uvicorn
asgi_app = WsgiToAsgi(app)

# Fallback to run as a Flask WSGI app directly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
