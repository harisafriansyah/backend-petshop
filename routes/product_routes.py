from flask import Blueprint
from controllers.ProductController import (
    get_public_products, 
    get_product_by_id, 
    search_and_filter_products,
    get_products_by_category,
    get_products_by_animal_type
)

product_bp = Blueprint('products', __name__)

# Routes untuk produk publik
product_bp.route('/', methods=['GET'])(get_public_products)  # Get all public products
product_bp.route('/<int:product_id>', methods=['GET'])(get_product_by_id)  # Get product by ID

# Route untuk search dan filter
product_bp.route('', methods=['GET'])(search_and_filter_products)

# Route untuk menampilkan produk berdasarkan kategori
product_bp.route('/category', methods=['GET'])(get_products_by_category)

# Route untuk menampilkan produk berdasarkan jenis hewan
product_bp.route('/animal', methods=['GET'])(get_products_by_animal_type)