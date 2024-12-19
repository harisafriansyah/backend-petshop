from flask import Blueprint
from controllers.WishlistController import add_to_wishlist, get_wishlist, remove_from_wishlist

wishlist_bp = Blueprint("wishlist", __name__)

wishlist_bp.route("/add", methods=["POST"])(add_to_wishlist)
wishlist_bp.route("/", methods=["GET"])(get_wishlist)
wishlist_bp.route("/<int:product_id>", methods=["DELETE"])(remove_from_wishlist)
