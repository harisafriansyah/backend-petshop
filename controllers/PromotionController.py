from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from connectors.db import db
from models.promotion import Promotion
from models.product import Product
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
        current_user = get_jwt_identity()
        if isinstance(current_user, str):
            current_user = json.loads(current_user)

        user_id = current_user.get("id")
        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 401

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
    """Update an existing promotion without requiring product_id."""
    try:
        # Ambil data JSON dari request
        data = request.get_json()
        
        # Pastikan data yang wajib dikirimkan
        required_fields = [
            "promotion_id", "promotion_name", "start_date", "end_date", 
            "start_time", "end_time", "max_quantity", "discount"
        ]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Validasi promotion data
        validation_error = validate_promotion_data(data)
        if validation_error:
            return jsonify({"msg": validation_error}), 400

        # Cari promotion berdasarkan ID
        promotion = Promotion.query.get(data["promotion_id"])
        if not promotion:
            return jsonify({"msg": "Promotion not found"}), 404

        # Update data promotion
        promotion.promotion_name = data["promotion_name"]
        promotion.promotion_period_start = datetime.strptime(
            data["start_date"] + " " + data["start_time"], "%Y-%m-%d %H:%M"
        )
        promotion.promotion_period_end = datetime.strptime(
            data["end_date"] + " " + data["end_time"], "%Y-%m-%d %H:%M"
        )
        promotion.max_quantity = int(data["max_quantity"])
        promotion.discount_percent = float(data["discount"])
        promotion.status = "active"  # Opsional: bisa diperbarui atau diatur otomatis

        # Simpan perubahan
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
    """Retrieve all promotions."""
    try:
        promotions = Promotion.query.all()
        return jsonify({"promotions": [promotion.to_dict() for promotion in promotions]}), 200
    except Exception as e:
        return jsonify({"msg": f"Error retrieving promotions: {str(e)}"}), 500


@jwt_required()
def assign_promotion_to_product():
    """Assign a promotion to a product."""
    try:
        data = request.get_json()
        required_fields = ["promotion_id", "product_id"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        promotion = Promotion.query.get(data["promotion_id"])
        if not promotion:
            return jsonify({"msg": "Promotion not found"}), 404

        product = Product.query.get(data["product_id"])
        if not product:
            return jsonify({"msg": "Product not found"}), 404

        # Assign promotion
        product.promotion_id = promotion.id
        db.session.commit()

        return jsonify({"msg": "Promotion assigned to product successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error assigning promotion: {str(e)}"}), 500


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
