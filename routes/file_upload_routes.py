from flask import Blueprint
from controllers.FileUploadController import upload_image

file_upload_bp = Blueprint("file_upload", __name__)

# Route untuk upload image
file_upload_bp.route("/upload-image", methods=["POST"])(upload_image)
