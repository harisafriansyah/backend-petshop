from flask import Blueprint, request, jsonify
from controllers.ProductController import create_product, get_products, get_product_by_id, update_product, delete_product

product_bp = Blueprint('products', __name__)

# Middleware for logging requests
@product_bp.before_request
def log_request():
    print(f"Incoming request: {request.method} {request.url}")

# Route untuk membuat produk
product_bp.route('/', methods=['POST'])(create_product)

# Route untuk mendapatkan semua produk
product_bp.route('/', methods=['GET'])(get_products)

# Route untuk mendapatkan produk berdasarkan ID
product_bp.route('/<int:product_id>', methods=['GET'])(get_product_by_id)

# Route untuk memperbarui produk
product_bp.route('/<int:product_id>', methods=['PUT'])(update_product)

# Route untuk menghapus produk
product_bp.route('/<int:product_id>', methods=['DELETE'])(delete_product)
