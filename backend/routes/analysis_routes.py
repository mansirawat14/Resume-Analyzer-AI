from flask import Blueprint, jsonify, request, send_file

from services.report_generator import generate_resume_report


analysis_bp = Blueprint(
    "analysis",
    __name__,
    url_prefix="/api/analysis"
)


@analysis_bp.route("/history", methods=["GET"])
def get_analysis_history():

    return jsonify({
        "success": True,
        "history": []
    }), 200


@analysis_bp.route("/download-report", methods=["POST"])
def download_report():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Analysis data is required."
        }), 400

    try:

        report = generate_resume_report(data)

        return send_file(
            report,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="ResuMate_Resume_Report.pdf"
        )

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Could not generate the resume report.",
            "error": str(e)
        }), 500