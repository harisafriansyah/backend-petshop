from flask import Blueprint
from controllers.ProductController import get_public_products, get_product_by_id

product_bp = Blueprint('products', __name__)

# Routes untuk produk publik
product_bp.route('/public-products', methods=['GET'])(get_public_products)  # Get all public products
product_bp.route('/<int:product_id>', methods=['GET'])(get_product_by_id)  # Get product by ID
