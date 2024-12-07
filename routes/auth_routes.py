from flask import Blueprint
from controllers.RegisterController import register_user, verify_otp, resend_otp

auth_bp = Blueprint('auth', __name__)

auth_bp.route('/register', methods=['POST'])(register_user)
auth_bp.route('/verify-otp', methods=['POST'])(verify_otp)
auth_bp.route('/resend-otp', methods=['POST'])(resend_otp)

