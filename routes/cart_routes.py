from flask import Blueprint
from controllers.CartController import add_to_cart, get_cart_items, update_cart_item, remove_from_cart

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

cart_bp.route('/add', methods=['POST'])(add_to_cart)
cart_bp.route('/items', methods=['GET'])(get_cart_items)
cart_bp.route('/update', methods=['PUT'])(update_cart_item)
cart_bp.route('/remove', methods=['DELETE'])(remove_from_cart)
