from flask import Blueprint
from controllers.ReviewController import create_review, get_reviews, get_review_detail, update_review

review_bp = Blueprint('review', __name__)

# Route untuk menambah ulasan
review_bp.route('/add', methods=['POST'])(create_review)

# Route untuk mendapatkan semua ulasan untuk produk tertentu
review_bp.route('/<int:product_id>', methods=['GET'])(get_reviews)

review_bp.route('/', methods=['GET'])(get_reviews)

# Route untuk mendapatkan detail ulasan tertentu
review_bp.route('//<int:review_id>', methods=['GET'])(get_review_detail)

# Route untuk memperbarui ulasan tertentu
review_bp.route('/<int:review_id>', methods=['PUT'])(update_review)
