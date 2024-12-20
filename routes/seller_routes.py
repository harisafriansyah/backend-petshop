from flask import Blueprint
from controllers.ProductController import (
    create_product,
    update_product,
    delete_product,
    get_seller_products
)
from controllers.SellerController import register_store
from controllers.CheckoutOrderController import update_order_status, seller_get_orders

seller_bp = Blueprint('seller', __name__)

# Route untuk register store
seller_bp.route('/register', methods=['POST'])(register_store)

# Routes untuk operasi produk seller
seller_bp.route('/create-products', methods=['POST'])(create_product)  # Create product
seller_bp.route('/products', methods=['GET'])(get_seller_products)  # Get seller products
seller_bp.route('/products/<int:product_id>', methods=['PUT'])(update_product)  # Update product
seller_bp.route('/products/<int:product_id>', methods=['DELETE'])(delete_product)  # Delete product

seller_bp.route('/order', methods=['GET'])(seller_get_orders)
seller_bp.route('/order/<int:order_id>/status', methods=['PUT'])(update_order_status)
