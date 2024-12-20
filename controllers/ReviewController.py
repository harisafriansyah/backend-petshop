from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from models.review import Review
from models.order import Order
from models.order_item import OrderItem
import json

@jwt_required()
def create_review():
    data = request.json

    # Ambil user identity dari JWT dan parsing jika berupa string JSON
    user_identity = get_jwt_identity()
    if isinstance(user_identity, str):  # Jika berupa string JSON
        user_identity = json.loads(user_identity)
    user_id = user_identity.get("id")  # Ambil hanya "id"

    # Validasi rating antara 1 dan 5
    if not (1 <= data['rating'] <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    # Validasi apakah produk dibeli oleh user dan status pembelian selesai
    product_id = data['product_id']
    order_item = OrderItem.query.join(Order).filter(
        Order.user_id == user_id,
        Order.status == "completed",  # Status "completed" menandakan pesanan selesai
        OrderItem.product_id == product_id
    ).first()

    if not order_item:
        return jsonify({"error": "You can only review products you have purchased and completed"}), 403

    # Cek apakah pengguna sudah memberikan ulasan untuk produk ini
    existing_review = Review.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing_review:
        return jsonify({"error": "You have already reviewed this product"}), 400

    # Buat ulasan baru
    new_review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=data['rating'],
        review=data.get('review', '')
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({"message": "Review added successfully!"}), 201
    

def get_reviews(product_id):
    # Dapatkan semua ulasan untuk produk tertentu
    reviews = Review.query.filter_by(product_id=product_id).all()
    return jsonify([review.to_dict() for review in reviews]), 200


def get_review_detail(review_id):
    # Dapatkan detail ulasan tertentu
    review = Review.query.options(joinedload('user')).filter_by(id=review_id).first()
    if not review:
        return jsonify({"error": "Review not found"}), 404

    return jsonify(review.to_dict()), 200


@jwt_required()
def update_review(review_id):
    user_id = get_jwt_identity()
    data = request.json

    # Validasi ulasan milik user
    review = Review.query.filter_by(id=review_id, user_id=user_id).first()
    if not review:
        return jsonify({"error": "Review not found or not authorized"}), 404

    # Perbarui rating dan review jika diberikan
    if 'rating' in data:
        if not (1 <= data['rating'] <= 5):
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
        review.rating = data['rating']

    if 'review' in data:
        review.review = data['review']

    db.session.commit()
    return jsonify({"message": "Review updated successfully!"}), 200
