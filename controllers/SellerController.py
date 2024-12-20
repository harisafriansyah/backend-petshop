from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from connectors.db import db
from models.store import Store
from models.user import User
from datetime import datetime
import json

@jwt_required()
def register_store():
    """
    Endpoint to register a new store for the logged-in user.
    """
    data = request.get_json()

    # Validate input
    required_fields = ["nama_toko", "nama_domain", "alamat_lengkap"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Get user info from token
    current_user = get_jwt_identity()

    # Decode current_user if it's a JSON string
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # Convert JSON string to dictionary

    user_id = current_user.get("id")
    if not user_id:
        return jsonify({"msg": "User ID not found in token"}), 401

    # Check if the user already has a store
    existing_store = Store.query.filter_by(user_id=user_id).first()
    if existing_store:
        return jsonify({"msg": "User already has a registered store"}), 400

    # Check if the domain is already taken
    existing_domain = Store.query.filter_by(nama_domain=data["nama_domain"]).first()
    if existing_domain:
        return jsonify({"msg": "Domain name is already taken"}), 400

    # Create a new store
    new_store = Store(
        user_id=user_id,
        nama_toko=data["nama_toko"],
        nama_domain=data["nama_domain"],
        alamat_lengkap=data["alamat_lengkap"],
        deskripsi_toko=data.get("deskripsi_toko", ""),
        created_at=datetime.utcnow()
    )
    db.session.add(new_store)

    # Update user to be a seller
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user.is_seller = True
    db.session.commit()

    return jsonify({"msg": "Store registered successfully", "status": "active"}), 201
