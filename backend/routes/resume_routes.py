import os

from flask import Blueprint, request, jsonify, current_app
from utils.file_handler import save_resume
from services.resume_parser import extract_resume_text


resume_bp = Blueprint(
    "resume",
    __name__,
    url_prefix="/api/resume"
)


@resume_bp.route("/upload", methods=["POST"])
def upload_resume():

    if "resume" not in request.files:
        return jsonify({
            "success": False,
            "message": "No resume file uploaded."
        }), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    filename = save_resume(
        file,
        current_app.config["UPLOAD_FOLDER"]
    )

    file_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        filename
    )

    resume_text = extract_resume_text(file_path)

    return jsonify({
        "success": True,
        "message": "Resume uploaded and text extracted successfully!",
        "filename": filename,
        "text_length": len(resume_text)
    }), 200