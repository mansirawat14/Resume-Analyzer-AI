from flask import Blueprint, request, jsonify, redirect, url_for, session
from flask import current_app

from extensions import oauth

from flask_jwt_extended import (
    JWTManager,
    create_access_token
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import timedelta
import secrets


# Create authentication blueprint
auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)

import secrets
# Temporary in-memory user storage
# This will later be replaced by your database teammate.
users = {}
reset_tokens = {}


# Register
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Validate fields
    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Name, email and password are required."
        }), 400

    # Check existing user
    if email in users:
        return jsonify({
            "success": False,
            "message": "An account with this email already exists."
        }), 409

    # Store hashed password
    users[email] = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password)
    }

    # Create JWT token
    access_token = create_access_token(
        identity=email
    )

    return jsonify({
        "success": True,
        "message": "Account created successfully.",
        "access_token": access_token,
        "user": {
            "name": name,
            "email": email
        }
    }), 201


# Login
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Validate fields
    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    # Find user
    user = users.get(email)

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    # Verify password
    if not check_password_hash(
        user["password"],
        password
    ):
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    # Create JWT token
    access_token = create_access_token(
        identity=email
    )

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "access_token": access_token,
        "user": {
            "name": user["name"],
            "email": user["email"]
        }
    }), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    if email not in users:
        return jsonify({
            "success": False,
            "message": "No account found with this email."
        }), 404

    # Generate a secure reset token
    reset_token = secrets.token_urlsafe(32)

    # Store token for this email
    reset_tokens[email] = reset_token

    return jsonify({
        "success": True,
        "message": "Password reset token generated successfully.",
        "reset_token": reset_token
    }), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    email = data.get("email", "").strip().lower()
    reset_token = data.get("reset_token", "")
    new_password = data.get("new_password", "")

    if not email or not reset_token or not new_password:
        return jsonify({
            "success": False,
            "message": "Email, reset token and new password are required."
        }), 400

    # Check whether the email has a reset token
    if email not in reset_tokens:
        return jsonify({
            "success": False,
            "message": "No password reset request found."
        }), 400

    # Check whether the token is correct
    if reset_tokens[email] != reset_token:
        return jsonify({
            "success": False,
            "message": "Invalid reset token."
        }), 400

    # Update the password
    users[email]["password"] = generate_password_hash(new_password)

    # Remove the token so it cannot be reused
    del reset_tokens[email]

    return jsonify({
        "success": True,
        "message": "Password reset successfully."
    }), 200

# Google Login
@auth_bp.route("/google/login", methods=["GET"])
def google_login():
    google = oauth.create_client("google")

    redirect_uri = url_for(
        "auth.google_callback",
        _external=True
    )

    return google.authorize_redirect(
        redirect_uri
    )
# Google Callback
@auth_bp.route("/google/callback", methods=["GET"])
def google_callback():
    google = oauth.create_client("google")

    token = google.authorize_access_token()

    user_info = token.get("userinfo")

    if not user_info:
        return jsonify({
            "success": False,
            "message": "Unable to retrieve Google account information."
        }), 400

    email = user_info.get("email", "").strip().lower()
    name = user_info.get("name") or user_info.get("given_name") or "Google User"

    if not email:
        return jsonify({
            "success": False,
            "message": "Google account email could not be retrieved."
        }), 400

    # Create user if they don't already exist
    if email not in users:
        users[email] = {
            "name": name,
            "email": email,
            "password": None,
            "provider": "google"
        }

    # Create ResuMate JWT
    access_token = create_access_token(
        identity=email
    )

    return jsonify({
        "success": True,
        "message": "Google login successful.",
        "access_token": access_token,
        "user": {
            "name": users[email]["name"],
            "email": email
        }
    }), 200