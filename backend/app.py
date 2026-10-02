from flask import Flask
from flask_cors import CORS
from config import Config

from flask_jwt_extended import JWTManager
from extensions import oauth

from routes.auth_routes import auth_bp
from routes.resume_routes import resume_bp
from routes.chatbot_routes import chatbot_bp
from routes.analysis_routes import analysis_bp


app = Flask(__name__)

# Load Resumate configuration
app.config.from_object(Config)
jwt = JWTManager(app)

oauth.init_app(app)

oauth.register(
    name="google",
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

# Enable CORS for frontend communication
CORS(app)

# Register resume routes
app.register_blueprint(auth_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(analysis_bp)

@app.route("/")
def home():
    return {
        "message": "Welcome to Resumate - AI Resume Analyzer!",
        "status": "Backend is running successfully"
    }


if __name__ == "__main__":
    app.run(debug=True)