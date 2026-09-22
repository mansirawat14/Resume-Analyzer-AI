from flask import Flask
from flask_cors import CORS
from config import Config
from routes.resume_routes import resume_bp


app = Flask(__name__)

# Load Resumate configuration
app.config.from_object(Config)

# Enable CORS for frontend communication
CORS(app)

# Register resume routes
app.register_blueprint(resume_bp)

@app.route("/")
def home():
    return {
        "message": "Welcome to Resumate - AI Resume Analyzer!",
        "status": "Backend is running successfully"
    }


if __name__ == "__main__":
    app.run(debug=True)