# === File: app/routes/health.py ===
# Health check route to confirm server is running
from flask import Blueprint

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health():
    return {"status": "OK"}, 200
