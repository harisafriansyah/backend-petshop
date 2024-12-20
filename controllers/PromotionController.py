from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from connectors.db import db
from models.promotion import Promotion
from models.product import Product
from models.store import Store
from models.user import User
from datetime import datetime
import json

def validate_promotion_data(data):
    """Helper function to validate promotion data."""
    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        if start_date >= end_date:
            return "Start date must be before end date"
        discount = float(data["discount"])
        if discount <= 0 or discount > 100:
            return "Discount percentage must be between 0 and 100"
        return None
    except ValueError as e:
        return f"Invalid date or format: {str(e)}"

@jwt_required()
def create_promotion():
    """Create a new promotion without requiring product_id."""
    try:
        # Ambil data user dari token JWT
        current_user = get_jwt_identity()
        if isinstance(current_user, str):
            current_user = json.loads(current_user)

        user_id = current_user.get("id")
        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 401

        # Query untuk mendapatkan user dan store
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404

        # Pastikan user memiliki toko
        if not user.stores or len(user.stores) == 0:
            return jsonify({"msg": "No store associated with this user"}), 403

        # Ambil store_id dari toko pertama (jika user hanya memiliki satu toko)
        store_id = user.stores[0].id

        # Data yang dikirimkan dari Frontend
        data = request.get_json()
        required_fields = [
            'promotion_name', 'start_date', 'end_date', 'start_time', 'end_time', 
            'max_quantity', 'discount'
        ]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Validasi promotion data
        validation_error = validate_promotion_data(data)
        if validation_error:
            return jsonify({"msg": validation_error}), 400

        # Buat objek Promotion
        new_promotion = Promotion(
            store_id=store_id,
            promotion_name=data['promotion_name'],
            promotion_period_start=datetime.strptime(data['start_date'] + " " + data['start_time'], "%Y-%m-%d %H:%M"),
            promotion_period_end=datetime.strptime(data['end_date'] + " " + data['end_time'], "%Y-%m-%d %H:%M"),
            max_quantity=int(data['max_quantity']),
            discount_percent=float(data['discount']),
            status="active"
        )
        db.session.add(new_promotion)
        db.session.commit()

        return jsonify({
            "msg": "Promotion created successfully",
            "promotion": new_promotion.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error creating promotion: {str(e)}"}), 500


@jwt_required()
def update_promotion():
    """Update an existing promotion created by the current user's store."""
    try:
        current_user = get_jwt_identity()
        if isinstance(current_user, str):
            current_user = json.loads(current_user)

        user_id = current_user.get("id")
        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404

        if not user.stores or len(user.stores) == 0:
            return jsonify({"msg": "No store associated with this user"}), 403

        store_id = user.stores[0].id

        data = request.get_json()
        required_fields = [
            "promotion_id", "promotion_name", "start_date", "end_date",
            "start_time", "end_time", "max_quantity", "discount"
        ]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        validation_error = validate_promotion_data(data)
        if validation_error:
            return jsonify({"msg": validation_error}), 400

        promotion = Promotion.query.get(data["promotion_id"])
        if not promotion:
            return jsonify({"msg": "Promotion not found"}), 404

        if promotion.store_id != store_id:
            return jsonify({"msg": "Unauthorized to update this promotion"}), 403

        promotion.promotion_name = data["promotion_name"]
        promotion.promotion_period_start = datetime.strptime(
            data["start_date"] + " " + data["start_time"], "%Y-%m-%d %H:%M"
        )
        promotion.promotion_period_end = datetime.strptime(
            data["end_date"] + " " + data["end_time"], "%Y-%m-%d %H:%M"
        )
        promotion.max_quantity = int(data["max_quantity"])
        promotion.discount_percent = float(data["discount"])

        db.session.commit()

        return jsonify({
            "msg": "Promotion updated successfully",
            "promotion": promotion.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error updating promotion: {str(e)}"}), 500


@jwt_required()
def get_all_promotions():
    """Retrieve all promotions created by the current user's store."""
    try:
        # Ambil identitas user dari token
        current_user = get_jwt_identity()
        if isinstance(current_user, str):
            current_user = json.loads(current_user)

        user_id = current_user.get("id")
        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 401

        # Query untuk mendapatkan user dan store
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404

        # Pastikan user memiliki toko
        if not user.stores or len(user.stores) == 0:
            return jsonify({"msg": "No store associated with this user"}), 403

        # Ambil store_id dari toko pertama (jika user hanya memiliki satu toko)
        store_id = user.stores[0].id

        # Query hanya untuk promotions yang dibuat oleh toko ini
        promotions = Promotion.query.filter_by(store_id=store_id).all()
        return jsonify({"promotions": [promotion.to_dict() for promotion in promotions]}), 200

    except Exception as e:
        return jsonify({"msg": f"Error retrieving promotions: {str(e)}"}), 500


@jwt_required()
def assign_promotion_to_product():
    """Assign a promotion to a product created by the current user's store."""
    try:
        # Ambil identitas user dari token
        current_user = get_jwt_identity()
        if isinstance(current_user, str):
            current_user = json.loads(current_user)

        user_id = current_user.get("id")
        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 401

        # Query untuk mendapatkan user dan store
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404

        # Pastikan user memiliki toko
        if not user.stores or len(user.stores) == 0:
            return jsonify({"msg": "No store associated with this user"}), 403

        # Ambil store_id dari toko pertama
        store_id = user.stores[0].id

        # Ambil data JSON dari request
        data = request.get_json()
        required_fields = ["promotion_id", "product_id"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        promotion_id = data["promotion_id"]
        product_id = data["product_id"]

        # Get Promotion
        promotion = Promotion.query.get(promotion_id)
        if not promotion:
            return jsonify({"msg": "Promotion not found"}), 404

        # Validasi apakah promotion milik toko ini
        if promotion.store_id != store_id:
            return jsonify({"msg": "Unauthorized to assign this promotion"}), 403

        # Get Product
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"msg": "Product not found"}), 404

        # Validasi apakah produk milik toko ini
        if product.store_id != store_id:
            return jsonify({"msg": "Unauthorized to assign promotion to this product"}), 403

        # Assign Promotion to Product
        promotion.product_id = product.id  # Update promotion_id in promotions table
        db.session.commit()

        return jsonify({
            "msg": "Promotion assigned to product successfully",
            "product_id": product.id,
            "promotion_id": promotion.id,
            "promotion_name": promotion.promotion_name
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error assigning promotion to product: {str(e)}"}), 500


@jwt_required()
def delete_promotion(promotion_id):
    """Delete a promotion."""
    try:
        promotion = Promotion.query.get(promotion_id)
        if not promotion:
            return jsonify({"msg": "Promotion not found"}), 404

        db.session.delete(promotion)
        db.session.commit()
        return jsonify({"msg": "Promotion deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error deleting promotion: {str(e)}"}), 500
