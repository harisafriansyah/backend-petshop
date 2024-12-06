from flask import Blueprint
from controllers.RegisterController import send_otp
from controllers.RegisterController import verify_otp

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp_route():
    return send_otp()

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp_route():
    return verify_otp()
