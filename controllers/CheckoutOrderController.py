from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from connectors.db import db
from models.cart import Cart
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from models.user import User
from models.order import Order
import json

# 1. Checkout Endpoint
@jwt_required()
def checkout():
    try:
        data = request.get_json()
        products = data.get('products')

        if not products:
            return jsonify({"message": "Products are required"}), 400

        # Parse JSON string dari get_jwt_identity()
        user_identity = json.loads(get_jwt_identity())
        user_id = user_identity["id"]

        total_price = 0
        order_items = []

        for item in products:
            if not item.get('product_id') or not item.get('quantity'):
                return jsonify({"message": "Each item must have product_id and quantity"}), 400

            product = Product.query.get(item['product_id'])
            if not product:
                return jsonify({"message": f"Product ID {item['product_id']} not found"}), 404

            # Validasi apakah produk dijual oleh toko pengguna
            if product.store.owner.id == user_id:  # Validasi pemilik toko
                return jsonify({
                    "message": f"You cannot purchase your own product: {product.nama_produk}"
                }), 400

            # Validasi stok produk
            if product.stok < item['quantity']:
                return jsonify({
                    "message": f"Product ID {item['product_id']} is not available or insufficient stock"
                }), 400

            # Kurangi stok produk
            product.stok -= item['quantity']
            total_price += product.harga * item['quantity']
            order_items.append(OrderItem(
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=product.harga * item['quantity']
            ))

        # Simpan pesanan
        order = Order(user_id=user_id, total_price=total_price, status='Pending')
        db.session.add(order)
        db.session.flush()

        # Simpan item pesanan
        for item in order_items:
            item.order_id = order.id
            db.session.add(item)

        db.session.commit()

        return jsonify({
            "message": "Order placed successfully",
            "order_id": order.id,
            "total_price": total_price,
            "created_at": order.created_at
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Error processing order", "error": str(e)}), 500


# 2. Daftar Pesanan Endpoint
@jwt_required()
def get_orders():
    try:
        # Parsing JSON string dari get_jwt_identity()
        user_identity = json.loads(get_jwt_identity())
        user_id = user_identity["id"]

        # Validasi user_id
        if not isinstance(user_id, int):
            return jsonify({"message": "Invalid user_id format"}), 400

        # Query untuk mendapatkan semua pesanan pengguna
        orders = Order.query.filter_by(user_id=user_id).all()

        return jsonify([{
            "order_id": order.id,
            "status": order.status,
            "total_price": order.total_price,
            "created_at": order.created_at
        } for order in orders]), 200

    except Exception as e:
        return jsonify({"message": "Error retrieving orders", "error": str(e)}), 500


# 3. Detail Pesanan Endpoint
@jwt_required()
def get_order(order_id):
    try:
        # Parsing JSON string dari get_jwt_identity()
        user_identity = json.loads(get_jwt_identity())
        user_id = user_identity["id"]

        # Validasi user_id
        if not isinstance(user_id, int):
            return jsonify({"message": "Invalid user_id format"}), 400

        # Query pesanan berdasarkan id dan user_id
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()

        if not order:
            return jsonify({"message": "Order not found"}), 404

        items = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price
            }
            for item in order.order_items
        ]

        return jsonify({
            "order_id": order.id,
            "status": order.status,
            "total_price": order.total_price,
            "created_at": order.created_at,
            "items": items
        }), 200

    except Exception as e:
        return jsonify({"message": "Error retrieving order details", "error": str(e)}), 500


# 4. Update Status Pesanan Endpoint
@jwt_required()
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get('status')

        # Validasi status yang valid
        if new_status not in ['Pending', 'Processing', 'Completed', 'Cancelled']:
            return jsonify({"message": "Invalid status"}), 400

        # Query untuk menemukan pesanan berdasarkan order_id
        order = Order.query.get(order_id)

        if not order:
            return jsonify({"message": "Order not found"}), 404

        # Perbarui status pesanan
        order.status = new_status
        db.session.commit()

        return jsonify({
            "message": "Order status updated successfully",
            "order_id": order.id,
            "new_status": new_status
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Error updating order status", "error": str(e)}), 500


# 5. Seller cek Order
@jwt_required()
def seller_get_orders():
    try:
        # Parsing JSON string dari `get_jwt_identity()`
        user_identity = json.loads(get_jwt_identity())
        user_id = user_identity["id"]

        # Validasi User
        user = User.query.get(user_id)
        print(f"Debug: user={user}")  # Log user
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Validasi apakah user adalah seller
        print(f"Debug: user.is_seller={user.is_seller}")  # Log is_seller
        if not user.is_seller:
            return jsonify({"message": "Only sellers can view their orders"}), 403

        # Validasi Stores
        stores = user.stores
        print(f"Debug: stores={stores}")  # Log stores
        if not stores:
            return jsonify({"message": "No stores found for this seller"}), 404

        product_ids = []
        for store in stores:
            product_ids.extend([product.id for product in store.products])

        # Query semua pesanan yang berisi produk seller
        order_items = OrderItem.query.filter(OrderItem.product_id.in_(product_ids)).all()
        orders = {}

        for item in order_items:
            order = item.order
            if order.id not in orders:
                orders[order.id] = {
                    "order_id": order.id,
                    "buyer_id": order.user_id,
                    "status": order.status,
                    "total_price": order.total_price,
                    "items": []
                }
            orders[order.id]["items"].append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price
            })

        return jsonify(list(orders.values())), 200

    except Exception as e:
        return jsonify({"message": "Error retrieving seller orders", "error": str(e)}), 500

@jwt_required()
def cancel_order(order_id):
    """
    Cancel an order if it is still in Pending or Processing status.
    """
    try:
        # Parsing JSON string dari get_jwt_identity()
        user_identity = json.loads(get_jwt_identity())
        user_id = user_identity["id"]

        # Query pesanan berdasarkan ID dan user ID
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()

        if not order:
            return jsonify({"message": "Order not found"}), 404

        # Validasi status pesanan
        if order.status == 'Completed':
            return jsonify({"message": "Completed orders cannot be cancelled"}), 400

        if order.status == 'Cancelled':
            return jsonify({"message": "Order is already cancelled"}), 400

        # Rollback stok produk dalam pesanan
        for item in order.order_items:
            product = Product.query.get(item.product_id)
            if product:
                product.stok += item.quantity

        # Perbarui status pesanan
        order.status = 'Cancelled'
        db.session.commit()

        return jsonify({
            "message": "Order cancelled successfully",
            "order_id": order.id,
            "status": order.status
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Error cancelling order", "error": str(e)}), 500
