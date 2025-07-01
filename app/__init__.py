from flask import Flask
from app.routes.agent_router import agent_bp

app = Flask(__name__, static_folder="static")
app.register_blueprint(agent_bp)

