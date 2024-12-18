from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from connectors.db import db
from models.cart import Cart
from models.product import Product  # Untuk validasi produk
import json

# Tambah produk ke keranjang
@jwt_required()
def add_to_cart():
    """
    Tambah produk ke keranjang.
    """
    # Ambil payload JWT
    current_user = get_jwt_identity()

    # Decode 'sub' jika diperlukan
    try:
        user_data = json.loads(current_user) if isinstance(current_user, str) else current_user
        user_id = user_data.get("id")
    except (ValueError, AttributeError):
        return jsonify({"msg": "User ID tidak valid."}), 400

    if not user_id:
        return jsonify({"msg": "User ID tidak valid."}), 400

    # Ambil data dari request
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    # Validasi input
    if not product_id or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"msg": "Produk ID dan jumlah harus valid."}), 400

    # Cek apakah produk ada
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Produk tidak ditemukan."}), 404

    # Cek apakah produk sudah ada di keranjang
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity  # Tambahkan jumlah jika sudah ada
    else:
        # Tambahkan produk baru ke keranjang
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    # Commit perubahan ke database
    db.session.commit()

    return jsonify({"msg": "Produk berhasil ditambahkan ke keranjang."}), 201


# Ambil semua item di keranjang
@jwt_required()
def get_cart_items():
    """
    Ambil semua item di keranjang pengguna.
    """
    # Ambil user_id dari JWT
    current_user = get_jwt_identity()

    # Decode 'sub' jika diperlukan
    try:
        user_data = json.loads(current_user) if isinstance(current_user, str) else current_user
        user_id = user_data.get("id")
    except (ValueError, AttributeError):
        return jsonify({"msg": "User ID tidak valid."}), 400

    if not user_id:
        return jsonify({"msg": "User ID tidak valid."}), 400

    # Query untuk mendapatkan item di keranjang
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    if not cart_items:
        return jsonify({"msg": "Keranjang kosong.", "cart": []}), 200

    # Format data keranjang
    cart_data = [
        {
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "product_details": {
                "name": item.product.nama_produk,
                "price": item.product.harga,
                "image_url": item.product.images[0].image_url if item.product.images else None
            }
        }
        for item in cart_items
    ]

    return jsonify({"msg": "Berhasil mendapatkan item di keranjang.", "cart": cart_data}), 200


# Update jumlah produk di keranjang
@jwt_required()
def update_cart_item():
    """
    Update jumlah produk di keranjang.
    """
    # Ambil user_id dari JWT
    current_user = get_jwt_identity()

    # Decode 'sub' jika diperlukan
    try:
        user_data = json.loads(current_user) if isinstance(current_user, str) else current_user
        user_id = user_data.get("id")
    except (ValueError, AttributeError):
        return jsonify({"msg": "User ID tidak valid."}), 400

    if not user_id:
        return jsonify({"msg": "User ID tidak valid."}), 400

    # Ambil data dari request
    data = request.get_json()
    cart_id = data.get("cart_id")
    quantity = data.get("quantity")

    # Validasi input
    if not cart_id or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"msg": "Keranjang ID dan jumlah harus valid."}), 400

    # Query untuk item di keranjang
    cart_item = Cart.query.filter_by(id=cart_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({"msg": "Item tidak ditemukan di keranjang."}), 404

    # Update jumlah item
    cart_item.quantity = quantity
    db.session.commit()

    return jsonify({"msg": "Jumlah item berhasil diperbarui."}), 200


# Hapus item dari keranjang
@jwt_required()
def remove_from_cart():
    """
    Hapus item dari keranjang.
    """
    # Ambil user_id dari JWT
    current_user = get_jwt_identity()

    # Decode 'sub' jika diperlukan
    try:
        user_data = json.loads(current_user) if isinstance(current_user, str) else current_user
        user_id = user_data.get("id")
    except (ValueError, AttributeError):
        return jsonify({"msg": "User ID tidak valid."}), 400

    if not user_id:
        return jsonify({"msg": "User ID tidak valid."}), 400

    # Ambil data dari request
    data = request.get_json()
    cart_id = data.get("cart_id")

    # Validasi input
    if not cart_id:
        return jsonify({"msg": "Keranjang ID harus diberikan."}), 400

    # Query untuk item di keranjang
    cart_item = Cart.query.filter_by(id=cart_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({"msg": "Item tidak ditemukan di keranjang."}), 404

    # Hapus item dari keranjang
    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({"msg": "Item berhasil dihapus dari keranjang."}), 200