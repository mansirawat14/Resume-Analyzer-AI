from flask import Flask
from flask_cors import CORS
from config import Config
from routes.resume_routes import resume_bp
from routes.chatbot_routes import chatbot_bp
from routes.analysis_routes import analysis_bp


app = Flask(__name__)

# Load Resumate configuration
app.config.from_object(Config)

# Enable CORS for frontend communication
CORS(app)

# Register resume routes
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