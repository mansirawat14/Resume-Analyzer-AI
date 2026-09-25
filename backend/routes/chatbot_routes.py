from flask import Blueprint, request, jsonify

from services.ai_service import generate_chatbot_response


chatbot_bp = Blueprint(
    "chatbot",
    __name__,
    url_prefix="/api/chatbot"
)


@chatbot_bp.route("/chat", methods=["POST"])
def chatbot():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    user_message = data.get(
        "message",
        ""
    ).strip()

    resume_data = data.get(
        "resume_data"
    )

    if not user_message:
        return jsonify({
            "success": False,
            "message": "Message is required."
        }), 400

    response = generate_chatbot_response(
        user_message,
        resume_data
    )

    return jsonify(response), 200
