from flask import Blueprint
from controllers.PromotionController import create_promotion, get_all_promotions, assign_promotion_to_product, update_promotion, delete_promotion

promotion_bp = Blueprint('promotion', __name__)

# Routes untuk operasi promotion
promotion_bp.route('/create', methods=['POST'])(create_promotion)  # Create promotion
promotion_bp.route('/assign', methods=['POST'])(assign_promotion_to_product)  # Assign promotion to product
promotion_bp.route('/', methods=['GET'])(get_all_promotions)  # Get all promotions
promotion_bp.route('/update', methods=['PUT'])(update_promotion)  # Update promotion
promotion_bp.route('//<int:promotion_id>', methods=['DELETE'])(delete_promotion)  # Delete promotion