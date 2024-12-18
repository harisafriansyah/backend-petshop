from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from connectors.db import db
from models.cart import Cart
from models.product import Product  # Untuk validasi produk

# Tambah produk ke keranjang
@jwt_required()
def add_to_cart():
    """
    Tambah produk ke keranjang.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id or quantity <= 0:
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
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"msg": "Produk berhasil ditambahkan ke keranjang."}), 201


# Ambil semua item di keranjang
@jwt_required()
def get_cart_items():
    """
    Ambil semua item di keranjang pengguna.
    """
    user_id = get_jwt_identity()
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    if not cart_items:
        return jsonify({"msg": "Keranjang kosong."}), 200

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
    user_id = get_jwt_identity()
    data = request.get_json()
    cart_id = data.get("cart_id")
    quantity = data.get("quantity")

    if not cart_id or quantity <= 0:
        return jsonify({"msg": "Keranjang ID dan jumlah harus valid."}), 400

    cart_item = Cart.query.filter_by(id=cart_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({"msg": "Item tidak ditemukan di keranjang."}), 404

    cart_item.quantity = quantity
    db.session.commit()
    return jsonify({"msg": "Jumlah item berhasil diperbarui."}), 200


# Hapus item dari keranjang
@jwt_required()
def remove_from_cart():
    """
    Hapus item dari keranjang.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    cart_id = data.get("cart_id")

    if not cart_id:
        return jsonify({"msg": "Keranjang ID harus diberikan."}), 400

    cart_item = Cart.query.filter_by(id=cart_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({"msg": "Item tidak ditemukan di keranjang."}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"msg": "Item berhasil dihapus dari keranjang."}), 200
