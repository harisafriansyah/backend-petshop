from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

def seller_required(f):
    """Middleware to ensure the user is a seller."""
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_seller:
            return jsonify({"status": "error", "message": "Seller access required"}), 403

        return f(*args, **kwargs)
    return wrapper
