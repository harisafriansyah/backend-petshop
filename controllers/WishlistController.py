from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wishlist import Wishlist
from models.product import Product
from connectors.db import db
import json

@jwt_required()
def add_to_wishlist():
    # Ambil user_id dari JWT
    raw_user_id = get_jwt_identity()
    try:
        # Cek jika raw_user_id berupa string JSON dan parse jika perlu
        user_data = json.loads(raw_user_id) if isinstance(raw_user_id, str) else raw_user_id
        user_id = user_data["id"] if isinstance(user_data, dict) else raw_user_id
    except (json.JSONDecodeError, KeyError, TypeError):
        return jsonify({"msg": "Invalid user identity in token"}), 401

    # Ambil data dari permintaan
    data = request.get_json()
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"msg": "Product ID is required"}), 400

    # Cek apakah produk ada
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Product not found"}), 404

    # Cek apakah produk sudah ada di wishlist
    existing_wishlist = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing_wishlist:
        return jsonify({"msg": "Product is already in the wishlist"}), 400

    # Tambahkan ke wishlist
    wishlist = Wishlist(user_id=user_id, product_id=product_id)
    db.session.add(wishlist)
    db.session.commit()

    return jsonify({"msg": "Product added to wishlist"}), 201

@jwt_required()
def get_wishlist():
    # Ambil user_id dari JWT
    raw_user_id = get_jwt_identity()
    try:
        user_data = json.loads(raw_user_id) if isinstance(raw_user_id, str) else raw_user_id
        user_id = user_data["id"] if isinstance(user_data, dict) else raw_user_id
    except (json.JSONDecodeError, KeyError, TypeError):
        return jsonify({"msg": "Invalid user identity in token"}), 401

    # Query semua produk dalam wishlist
    wishlist_items = (
        db.session.query(Wishlist, Product)
        .join(Product, Wishlist.product_id == Product.id)
        .filter(Wishlist.user_id == user_id)
        .all()
    )

    if not wishlist_items:
        return jsonify({"msg": "Your wishlist is empty"}), 404

    # Format respons
    wishlist = [
        {
            "wishlist_id": item.Wishlist.id,
            "product_id": item.Product.id,
            "product_name": item.Product.nama_produk,
            "product_price": item.Product.harga,
            "product_images": [{"url": img.image_url} for img in item.Product.images],
        }
        for item in wishlist_items
    ]

    return jsonify({"msg": "Wishlist retrieved successfully", "wishlist": wishlist}), 200

@jwt_required()
def remove_from_wishlist(product_id):
    # Ambil user_id dari JWT
    raw_user_id = get_jwt_identity()
    try:
        user_data = json.loads(raw_user_id) if isinstance(raw_user_id, str) else raw_user_id
        user_id = user_data["id"] if isinstance(user_data, dict) else raw_user_id
    except (json.JSONDecodeError, KeyError, TypeError):
        return jsonify({"msg": "Invalid user identity in token"}), 401

    # Cek apakah produk ada di wishlist
    wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not wishlist_item:
        return jsonify({"msg": "Product not found in wishlist"}), 404

    # Hapus produk dari wishlist
    db.session.delete(wishlist_item)
    db.session.commit()

    return jsonify({"msg": "Product removed from wishlist"}), 200
