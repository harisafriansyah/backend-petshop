from flask import Blueprint
from controllers.ProductController import (
    create_product,
    update_product,
    delete_product,
    get_seller_products
)
from controllers.SellerController import register_store

seller_bp = Blueprint('seller', __name__)

# Route untuk register store
seller_bp.route('/register', methods=['POST'])(register_store)

# Routes untuk operasi produk seller
seller_bp.route('/create-products', methods=['POST'])(create_product)  # Create product
seller_bp.route('/products', methods=['GET'])(get_seller_products)  # Get seller products
seller_bp.route('/products/<int:product_id>', methods=['PUT'])(update_product)  # Update product
seller_bp.route('/products/<int:product_id>', methods=['DELETE'])(delete_product)  # Delete product
