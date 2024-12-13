from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from connectors.db import db
from models.user import User

@jwt_required()
def get_user_details():
    """
    Retrieve the details of the currently logged-in user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    return jsonify({
        "status": "success",
        "data": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        }
    }), 200

@jwt_required()
def update_user_profile():
    """
    Update the profile of the currently logged-in user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    data = request.get_json()
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)

    db.session.commit()
    return jsonify({"status": "success", "message": "Profile updated successfully"}), 200

@jwt_required()
def get_role_status():
    """
    Retrieve the current role of the logged-in user.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    return jsonify({
        "status": "success",
        "data": {
            "role": user.role
        }
    }), 200