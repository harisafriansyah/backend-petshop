from flask import request, jsonify
import cloudinary.uploader

def upload_image():
    """
    Upload an image to Cloudinary.
    """
    if 'file' not in request.files:
        return jsonify({"msg": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    try:
        # Upload file ke Cloudinary
        result = cloudinary.uploader.upload(file, folder="ecommerce/uploads")
        return jsonify({
            "msg": "File uploaded successfully",
            "url": result['secure_url']
        }), 200
    except Exception as e:
        return jsonify({"msg": f"Failed to upload image: {str(e)}"}), 500
