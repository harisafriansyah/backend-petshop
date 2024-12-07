from flask import Blueprint
from controllers.RegisterController import register_user, verify_otp, resend_otp
from controllers.LoginController import login, refresh_token, logout

auth_bp = Blueprint('auth', __name__)

# Register routes
auth_bp.route('/register', methods=['POST'])(register_user)
auth_bp.route('/verify-otp', methods=['POST'])(verify_otp)
auth_bp.route('/resend-otp', methods=['POST'])(resend_otp)

# Login routes
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/refresh-token', methods=['POST'])(refresh_token)
auth_bp.route('/logout', methods=['POST'])(logout)
