from flask import request, jsonify, current_app
from connectors.db import db  # Database connector
from models.user import User  # User model
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta

def create_token(data, expires_in):
    """Generate JWT token with expiration."""
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_in)
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

def decode_token(token):
    """Decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"], None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"

# Login endpoint
def login():
    """Handle user login."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validasi input
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    # Cari pengguna berdasarkan email
    user = User.query.filter_by(email=email).first()
    if not user:
        current_app.logger.warning(f"Login failed: User not found for email {email}")
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    # Check password hash
    if not check_password_hash(user.password_hash, password):
        current_app.logger.warning(f"Login failed: Incorrect password for email {email}")
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    # Generate tokens
    access_token = create_token({"id": user.id, "email": user.email}, ACCESS_TOKEN_EXPIRES)
    refresh_token = create_token({"id": user.id, "email": user.email}, REFRESH_TOKEN_EXPIRES * 24 * 60)

    return jsonify({
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "message": "Login successful"
    }), 200

# Refresh token endpoint
def refresh_token():
    """Generate a new access token using a valid refresh token."""
    data = request.get_json()
    if not data or not data.get("refresh_token"):
        return jsonify({"status": "error", "message": "Refresh token is required"}), 400

    token = data.get("refresh_token")
    user_data, error = decode_token(token)

    if error:
        return jsonify({"status": "error", "message": error}), 401

    # Generate a new access token
    access_token = create_token(user_data, ACCESS_TOKEN_EXPIRES)

    return jsonify({
        "status": "success",
        "access_token": access_token,
        "message": "Access token refreshed"
    }), 200

# Logout endpoint (optional)
def logout():
    """Invalidate refresh token by removing it from the database (if stored)."""
    # If refresh tokens are stored in the database, handle token removal here.
    return jsonify({
        "status": "success",
        "message": "Logged out successfully"
    }), 200
