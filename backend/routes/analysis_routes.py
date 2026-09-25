from flask import Blueprint, jsonify

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
