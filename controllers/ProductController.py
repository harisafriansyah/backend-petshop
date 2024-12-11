from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from connectors.db import db
from models.product import Product
from models.store import Store
from datetime import datetime
import json

@jwt_required()
def create_product():
    """
    Create a new product for the logged-in user's store.
    """
    # Ambil data pengguna dari token JWT
    current_user = get_jwt_identity()

    # Debug log untuk memastikan identitas pengguna
    current_app.logger.info(f"Current User Raw Data: {current_user}")

    # Validasi dan dekode nilai current_user
    if isinstance(current_user, str):
        try:
            current_user = json.loads(current_user)
        except json.JSONDecodeError:
            current_app.logger.error("Failed to decode user identity from token")
            return jsonify({"msg": "Invalid user identity in token"}), 400

    if not isinstance(current_user, dict):
        current_app.logger.error("User identity is not a valid dictionary")
        return jsonify({"msg": "Invalid user identity in token"}), 400

    user_id = current_user.get("id")
    if not user_id:
        current_app.logger.error("User ID not found in token")
        return jsonify({"msg": "User ID not found in token"}), 401

    # Pastikan pengguna memiliki toko
    store = Store.query.filter_by(user_id=user_id).first()
    if not store:
        return jsonify({"msg": "You don't have a registered store"}), 403

    data = request.get_json()

    # Validasi field yang diperlukan
    required_fields = ["nama_produk", "harga", "stok", "kategori", "jenis_hewan"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Validasi kategori dan jenis_hewan
    valid_categories = ["makanan", "kesehatan", "mainan", "peralatan"]
    valid_animals = ["anjing", "kucing", "hamster", "burung", "kelinci"]

    if data["kategori"] not in valid_categories:
        return jsonify({"msg": f"Invalid category. Valid options: {', '.join(valid_categories)}"}), 400

    if data["jenis_hewan"] not in valid_animals:
        return jsonify({"msg": f"Invalid animal type. Valid options: {', '.join(valid_animals)}"}), 400

    # Validasi harga dan stok
    if not isinstance(data["harga"], (int, float)) or data["harga"] <= 0:
        return jsonify({"msg": "Harga harus berupa angka positif"}), 400

    if not isinstance(data["stok"], int) or data["stok"] < 0:
        return jsonify({"msg": "Stok harus berupa bilangan bulat positif"}), 400

    # Buat dan simpan produk baru
    new_product = Product(
        nama_produk=data["nama_produk"],
        deskripsi=data.get("deskripsi", ""),
        harga=data["harga"],
        stok=data["stok"],
        gambar=data.get("gambar"),
        kategori=data["kategori"],
        jenis_hewan=data["jenis_hewan"],
        store_id=store.id,
        created_at=datetime.utcnow()
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({"msg": "Product created successfully", "product": new_product.nama_produk}), 201

@jwt_required()
def get_products():
    """
    Endpoint to retrieve all products for the logged-in user's store.
    """
    current_user = get_jwt_identity()
    if isinstance(current_user, str):
        current_user = json.loads(current_user)
    user_id = current_user.get("id")

    store = Store.query.filter_by(user_id=user_id).first()
    if not store:
        return jsonify({"msg": "You don't have a registered store"}), 403

    products = Product.query.filter_by(store_id=store.id).all()
    if not products:
        return jsonify({"msg": "No products found"}), 404

    products_list = [
        {
            "id": product.id,
            "nama_produk": product.nama_produk,
            "deskripsi": product.deskripsi,
            "harga": product.harga,
            "stok": product.stok,
            "gambar": product.gambar,
            "kategori": product.kategori,
            "jenis_hewan": product.jenis_hewan,
            "store_id": product.store_id
        }
        for product in products
    ]
    return jsonify({"msg": "Products retrieved successfully", "products": products_list}), 200

@jwt_required()
def get_product_by_id(product_id):
    """
    Endpoint to retrieve a product by its ID.
    """
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Product not found"}), 404

    product_data = {
        "id": product.id,
        "nama_produk": product.nama_produk,
        "deskripsi": product.deskripsi,
        "harga": product.harga,
        "stok": product.stok,
        "gambar": product.gambar,
        "kategori": product.kategori,
        "jenis_hewan": product.jenis_hewan,
        "store_id": product.store_id
    }
    return jsonify({"msg": "Product retrieved successfully", "product": product_data}), 200

@jwt_required()
def update_product(product_id):
    """
    Endpoint to update an existing product by its ID.
    """
    current_user = get_jwt_identity()
    if isinstance(current_user, str):
        current_user = json.loads(current_user)
    user_id = current_user.get("id")

    store = Store.query.filter_by(user_id=user_id).first()
    if not store:
        return jsonify({"msg": "You don't have a registered store"}), 403

    product = Product.query.get(product_id)
    if not product or product.store_id != store.id:
        return jsonify({"msg": "Unauthorized to update this product"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"msg": "No input data provided"}), 400

    product.nama_produk = data.get("nama_produk", product.nama_produk)
    product.deskripsi = data.get("deskripsi", product.deskripsi)
    product.harga = data.get("harga", product.harga)
    product.stok = data.get("stok", product.stok)
    product.gambar = data.get("gambar", product.gambar)
    product.kategori = data.get("kategori", product.kategori)
    product.jenis_hewan = data.get("jenis_hewan", product.jenis_hewan)

    db.session.commit()

    return jsonify({"msg": "Product updated successfully"}), 200

@jwt_required()
def delete_product(product_id):
    """
    Endpoint to delete a product by its ID.
    """
    current_user = get_jwt_identity()
    if isinstance(current_user, str):
        current_user = json.loads(current_user)
    user_id = current_user.get("id")

    store = Store.query.filter_by(user_id=user_id).first()
    if not store:
        return jsonify({"msg": "You don't have a registered store"}), 403

    product = Product.query.get(product_id)
    if not product or product.store_id != store.id:
        return jsonify({"msg": "Unauthorized to delete this product"}), 403

    db.session.delete(product)
    db.session.commit()

    return jsonify({"msg": "Product deleted successfully"}), 200
