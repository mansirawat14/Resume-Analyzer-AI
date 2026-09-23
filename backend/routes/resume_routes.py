from flask import Blueprint, request, jsonify, current_app

from utils.file_handler import save_resume
from services.resume_parser import extract_resume_text
from services.resume_analyzer import analyze_resume


# ============================================================
# RESUME BLUEPRINT
# ============================================================

resume_bp = Blueprint(
    "resume",
    __name__,
    url_prefix="/api/resume"
)


# ============================================================
# UPLOAD RESUME
# ============================================================

@resume_bp.route("/upload", methods=["POST"])
def upload_resume():

    # Check if resume file was provided
    if "resume" not in request.files:
        return jsonify({
            "success": False,
            "message": "No resume file uploaded."
        }), 400

    file = request.files["resume"]

    # Check filename
    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    # Save resume
    filename = save_resume(
        file,
        current_app.config["UPLOAD_FOLDER"]
    )

    # Create complete path
    file_path = (
        current_app.config["UPLOAD_FOLDER"]
        + "/"
        + filename
    )

    # Extract text
    try:
        text = extract_resume_text(
            file_path
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Could not extract resume text.",
            "error": str(e)
        }), 500

    # ========================================================
    # ANALYZE RESUME
    # ========================================================

    try:

        # Optional job description
        job_description = request.form.get(
            "job_description",
            ""
        ).strip()

        analysis = analyze_resume(
            text,
            job_description=job_description
            if job_description
            else None
        )

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Resume analysis failed.",
            "error": str(e)
        }), 500

    # Add upload information
    analysis["filename"] = filename
    analysis["text_length"] = len(text)

    # Return complete analysis
    return jsonify(
        analysis
    ), 200