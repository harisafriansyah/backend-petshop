from flask import Blueprint, jsonify
from controllers.UserController import get_user_details, update_user_profile

user_bp = Blueprint('user', __name__)

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return get_user_details(user_id)

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return update_user_profile(user_id)
