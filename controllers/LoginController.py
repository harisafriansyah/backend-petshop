from flask import request, jsonify, current_app
from connectors.db import db  # Database connector
from models.user import User  # User model
from werkzeug.security import check_password_hash
import jwt, json
from datetime import datetime, timedelta


# Helper function to create JWT
def create_token(data, expires_in):
    """
    Generate a JWT token with expiration.
    :param data: Payload to include in the token.
    :param expires_in: Expiration time in minutes.
    :return: Encoded JWT token.
    """
    payload = {
        "exp": datetime.utcnow() + timedelta(minutes=expires_in),
        "iat": datetime.utcnow(),
        "sub": json.dumps(data)  # Convert dictionary to JSON string
    }
    current_app.logger.info(f"Creating token with payload: {payload}")
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

# Helper function to decode JWT
def decode_token(token):
    """
    Decode a JWT token.
    :param token: JWT token to decode.
    :return: Decoded payload or error message.
    """
    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        payload["sub"] = json.loads(payload["sub"])  # Convert JSON string back to dictionary
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


# Login endpoint
def login():
    """
    Handle user login.
    :return: JSON response with access and refresh tokens.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        current_app.logger.warning(f"Login failed for email: {email}")
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    access_token_expires = int(current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 15))
    refresh_token_expires = int(current_app.config.get("JWT_REFRESH_TOKEN_EXPIRES", 7 * 24 * 60))

    access_token = create_token({"id": user.id, "email": user.email}, access_token_expires)
    refresh_token = create_token({"id": user.id, "email": user.email}, refresh_token_expires)

    return jsonify({
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "message": "Login successful"
    }), 200


# Refresh token endpoint
def refresh_token():
    """
    Generate a new access token using a valid refresh token.
    :return: JSON response with new access token.
    """
    data = request.get_json()
    token = data.get("refresh_token")

    if not token:
        return jsonify({"status": "error", "message": "Refresh token is required"}), 400

    user_data, error = decode_token(token)
    if error:
        current_app.logger.error(f"Token decoding error: {error}")
        return jsonify({"status": "error", "message": error}), 401

    access_token_expires = int(current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 15))
    access_token = create_token(user_data["sub"], access_token_expires)

    return jsonify({
        "status": "success",
        "access_token": access_token,
        "message": "Access token refreshed"
    }), 200


# Logout endpoint
def logout():
    """
    Handle logout by invalidating the refresh token (if implemented).
    :return: JSON response confirming logout.
    """
    return jsonify({
        "status": "success",
        "message": "Logged out successfully"
    }), 200


# Check refresh token endpoint
def check_refresh_token():
    """
    Validate the refresh token.
    :return: JSON response with token validation status.
    """
    data = request.get_json()
    token = data.get("refresh_token")

    if not token:
        return jsonify({"status": "error", "message": "Refresh token is required"}), 400

    payload, error = decode_token(token)
    if error:
        return jsonify({"status": "error", "message": error}), 401

    return jsonify({
        "status": "success",
        "message": "Token is valid",
        "payload": payload
    }), 200
