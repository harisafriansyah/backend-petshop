from flask import Blueprint
from controllers.CheckoutOrderController import get_orders, get_order

# Membuat blueprint untuk order
order_bp = Blueprint('order', __name__, url_prefix='/order')

# Definisi route
order_bp.route('/', methods=['GET'])(get_orders)
order_bp.route('/<int:order_id>', methods=['GET'])(get_order)
