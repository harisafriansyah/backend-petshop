from flask import Blueprint
from controllers.SellerController import register_store

seller_bp = Blueprint('seller', __name__)

seller_bp.route('/register', methods=['POST'])(register_store)
