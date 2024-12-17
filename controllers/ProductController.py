from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from connectors.db import db
from models.product import Product
from models.product_image import ProductImage
from models.store import Store
from datetime import datetime
import cloudinary.uploader
import json
from sqlalchemy import or_

def search_and_filter_products():
    """
    Search and filter products based on query parameters.
    """
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'nama_produk')
    order = request.args.get('order', 'asc')

    query = Product.query

    if search:
        query = query.filter(
            or_(
                Product.nama_produk.ilike(f"%{search}%"),
                Product.deskripsi.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter(Product.kategori == category)

    if min_price is not None:
        query = query.filter(Product.harga >= min_price)
    if max_price is not None:
        query = query.filter(Product.harga <= max_price)

    if sort_by in ['harga', 'nama_produk']:
        query = query.order_by(
            getattr(Product, sort_by).desc() if order == 'desc' else getattr(Product, sort_by).asc()
        )

    products = query.all()

    if not products:
        return jsonify({"msg": "No products found"}), 404

    products_list = [
        {
            "id": product.id,
            "nama_produk": product.nama_produk,
            "deskripsi": product.deskripsi,
            "harga": product.harga,
            "stok": product.stok,
            "images": [{"id": img.id, "url": img.image_url} for img in product.images],
            "kategori": product.kategori,
            "jenis_hewan": product.jenis_hewan,
            "berat": product.berat,
            "ukuran": {
                "panjang": product.panjang,
                "lebar": product.lebar,
                "tinggi": product.tinggi,
            },
        }
        for product in products
    ]

    return jsonify({"msg": "Products retrieved successfully", "products": products_list}), 200

# Public endpoint to retrieve all products
def get_public_products():
    """
    Retrieve all public products.
    """
    products = Product.query.all()
    if not products:
        return jsonify({"msg": "No products found"}), 404

    products_list = [
        {
            "id": product.id,
            "nama_produk": product.nama_produk,
            "deskripsi": product.deskripsi,
            "harga": product.harga,
            "stok": product.stok,
            "images": [{"id": img.id, "url": img.image_url} for img in product.images],
            "kategori": product.kategori,
            "jenis_hewan": product.jenis_hewan,
            "berat": product.berat,
            "ukuran": {
                "panjang": product.panjang,
                "lebar": product.lebar,
                "tinggi": product.tinggi,
            },
        }
        for product in products
    ]
    return jsonify({"msg": "Public products retrieved successfully", "products": products_list}), 200


# Public or seller-specific endpoint to retrieve a product by ID
def get_product_by_id(product_id):
    """
    Retrieve a specific product by its ID.
    """
    user_data = None
    try:
        verify_jwt_in_request(optional=True)
        user_data = get_jwt_identity()
        if isinstance(user_data, str):
            user_data = json.loads(user_data)
    except Exception as e:
        current_app.logger.info(f"No token provided or invalid token: {str(e)}")

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Product not found"}), 404

    is_seller = False
    if user_data:
        store = Store.query.filter_by(user_id=user_data.get("id")).first()
        is_seller = store and store.id == product.store_id

    product_data = {
        "id": product.id,
        "nama_produk": product.nama_produk,
        "deskripsi": product.deskripsi,
        "harga": product.harga,
        "stok": product.stok,
        "images": [{"id": img.id, "url": img.image_url} for img in product.images],
        "kategori": product.kategori,
        "jenis_hewan": product.jenis_hewan,
        "berat": product.berat,
        "ukuran": {
            "panjang": product.panjang,
            "lebar": product.lebar,
            "tinggi": product.tinggi,
        },
        "actions": {
            "can_edit": is_seller,
            "can_purchase": not is_seller
        },
    }
    return jsonify({"msg": "Product retrieved successfully", "product": product_data}), 200


# Create a new product
@jwt_required()
def create_product():
    """
    Create a new product for the logged-in user's store.
    """
    current_user = get_jwt_identity()
    if isinstance(current_user, str):
        current_user = json.loads(current_user)

    user_id = current_user.get("id")
    if not user_id:
        return jsonify({"msg": "User ID not found in token"}), 401

    store = Store.query.filter_by(user_id=user_id).first()
    if not store:
        return jsonify({"msg": "You don't have a registered store"}), 403

    data = request.form.to_dict()
    required_fields = ["nama_produk", "harga", "stok", "kategori", "jenis_hewan", "berat"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"msg": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    valid_categories = ["makanan", "kesehatan", "mainan", "peralatan"]
    valid_animals = ["anjing", "kucing", "hamster", "burung", "kelinci"]

    if data["kategori"] not in valid_categories:
        return jsonify({"msg": f"Invalid category. Valid options: {', '.join(valid_categories)}"}), 400
    if data["jenis_hewan"] not in valid_animals:
        return jsonify({"msg": f"Invalid animal type. Valid options: {', '.join(valid_animals)}"}), 400

    # Validate numeric fields
    try:
        data["harga"] = float(data["harga"])
        data["stok"] = int(data["stok"])
        data["berat"] = float(data["berat"])
        data["panjang"] = float(data.get("panjang", 0)) if data.get("panjang") else None
        data["lebar"] = float(data.get("lebar", 0)) if data.get("lebar") else None
        data["tinggi"] = float(data.get("tinggi", 0)) if data.get("tinggi") else None
    except ValueError:
        return jsonify({"msg": "Invalid numeric value for harga, stok, or berat"}), 400

    # Create new product
    new_product = Product(
        nama_produk=data["nama_produk"],
        deskripsi=data.get("deskripsi", ""),
        harga=data["harga"],
        stok=data["stok"],
        kategori=data["kategori"],
        jenis_hewan=data["jenis_hewan"],
        berat=data["berat"],
        panjang=data["panjang"],
        lebar=data["lebar"],
        tinggi=data["tinggi"],
        store_id=store.id,
        created_at=datetime.utcnow()
    )
    db.session.add(new_product)
    db.session.commit()

    # Upload images
    product_images = []
    if "images" in request.files:
        images = request.files.getlist("images")
        for image in images:
            try:
                result = cloudinary.uploader.upload(image)
                image_url = result["secure_url"]

                # Save image to database
                product_image = ProductImage(
                    product_id=new_product.id,
                    image_url=image_url
                )
                db.session.add(product_image)
                product_images.append({"id": product_image.id, "url": image_url})
            except Exception as e:
                current_app.logger.error(f"Failed to upload image: {e}")
                return jsonify({"msg": f"Failed to upload image: {str(e)}"}), 500

    db.session.commit()

    return jsonify({
        "msg": "Product created successfully",
        "product": {
            "id": new_product.id,
            "nama_produk": new_product.nama_produk,
            "images": product_images
        }
    }), 201

@jwt_required()
def get_seller_products():
    """
    Retrieve products for the logged-in seller's store.
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
        return jsonify({"msg": "No products found for your store"}), 404

    products_list = [
        {
            "id": product.id,
            "nama_produk": product.nama_produk,
            "deskripsi": product.deskripsi,
            "harga": product.harga,
            "stok": product.stok,
            "images": [{"id": img.id, "url": img.image_url} for img in product.images],
            "kategori": product.kategori,
            "jenis_hewan": product.jenis_hewan,
            "berat": product.berat,
            "ukuran": {
                "panjang": product.panjang,
                "lebar": product.lebar,
                "tinggi": product.tinggi,
            },
        }
        for product in products
    ]
    return jsonify({"msg": "Seller products retrieved successfully", "products": products_list}), 200

@jwt_required()
def update_product(product_id):
    """
    Update an existing product by its ID.
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

    data = request.form.to_dict()

    # Update product attributes
    product.nama_produk = data.get("nama_produk", product.nama_produk)
    product.deskripsi = data.get("deskripsi", product.deskripsi)
    product.harga = float(data.get("harga", product.harga))
    product.stok = int(data.get("stok", product.stok))
    product.kategori = data.get("kategori", product.kategori)
    product.jenis_hewan = data.get("jenis_hewan", product.jenis_hewan)
    product.berat = float(data.get("berat", product.berat))
    product.panjang = float(data.get("panjang", product.panjang)) if data.get("panjang") else product.panjang
    product.lebar = float(data.get("lebar", product.lebar)) if data.get("lebar") else product.lebar
    product.tinggi = float(data.get("tinggi", product.tinggi)) if data.get("tinggi") else product.tinggi

    # Handle new images if provided
    if "images" in request.files:
        images = request.files.getlist("images")
        # Delete existing images if new ones are uploaded
        for img in product.images:
            db.session.delete(img)

        for image in images:
            try:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(image)
                image_url = result["secure_url"]

                # Save the new image to ProductImage
                product_image = ProductImage(
                    product_id=product.id,
                    image_url=image_url
                )
                db.session.add(product_image)
            except Exception as e:
                current_app.logger.error(f"Failed to upload image: {e}")
                return jsonify({"msg": f"Failed to upload image: {str(e)}"}), 500

    db.session.commit()

    # Fetch all updated images for the product
    product_images = [{"id": img.id, "url": img.image_url} for img in product.images]

    return jsonify({
        "msg": "Product updated successfully",
        "product": {
            "id": product.id,
            "nama_produk": product.nama_produk,
            "images": product_images
        }
    }), 200

@jwt_required()
def delete_product(product_id):
    """
    Delete a product by its ID.
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
