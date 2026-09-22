from flask import Blueprint, request, jsonify


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

    return jsonify({
        "success": True,
        "message": "Resume received successfully!",
        "filename": file.filename
    }), 200
