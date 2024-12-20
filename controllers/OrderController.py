from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from models import db, Product, Order, OrderItem, User

# 1. Checkout Endpoint
@jwt_required()
def checkout():
    """
    Buyer melakukan checkout pesanan.
    """
    try:
        data = request.get_json()
        products = data.get('products')  # [{product_id: 1, quantity: 2}, ...]

        if not products:
            return jsonify({"message": "Products are required"}), 400

        user_id = get_jwt_identity()
        total_price = 0
        order_items = []

        # Validasi stok produk dan hitung total harga
        for item in products:
            product = Product.query.get(item['product_id'])
            if not product or product.stock < item['quantity']:
                return jsonify({
                    "message": f"Product ID {item['product_id']} is not available or insufficient stock"
                }), 400

            # Kurangi stok produk
            product.stock -= item['quantity']
            total_price += product.price * item['quantity']
            order_items.append(OrderItem(
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=product.price * item['quantity']
            ))

        # Simpan pesanan
        order = Order(user_id=user_id, total_price=total_price, status='Pending')
        db.session.add(order)
        db.session.flush()  # Dapatkan ID pesanan

        # Simpan item pesanan
        for item in order_items:
            item.order_id = order.id
            db.session.add(item)

        db.session.commit()

        return jsonify({
            "message": "Order placed successfully",
            "order_id": order.id,
            "total_price": total_price
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "Error processing order", "error": str(e)}), 500

# 2. Daftar Pesanan Endpoint
@jwt_required()
def get_orders():
    """
    Mendapatkan daftar pesanan untuk pengguna yang sedang login.
    """
    try:
        user_id = get_jwt_identity()
        orders = Order.query.filter_by(user_id=user_id).all()

        return jsonify([{
            "order_id": order.id,
            "status": order.status,
            "total_price": order.total_price,
            "created_at": order.created_at
        } for order in orders]), 200

    except SQLAlchemyError as e:
        return jsonify({"message": "Error retrieving orders", "error": str(e)}), 500


# 3. Detail Pesanan Endpoint
@jwt_required()
def get_order(order_id):
    """
    Mendapatkan detail pesanan berdasarkan ID pesanan.
    """
    try:
        user_id = get_jwt_identity()
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()

        if not order:
            return jsonify({"message": "Order not found"}), 404

        items = OrderItem.query.filter_by(order_id=order.id).all()
        item_details = [{
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": item.price
        } for item in items]

        return jsonify({
            "order_id": order.id,
            "status": order.status,
            "total_price": order.total_price,
            "items": item_details,
            "created_at": order.created_at
        }), 200

    except SQLAlchemyError as e:
        return jsonify({"message": "Error retrieving order details", "error": str(e)}), 500


# 4. Update Status Pesanan Endpoint
@jwt_required()
def update_order_status(order_id):
    """
    Mengubah status pesanan berdasarkan ID pesanan.
    """
    try:
        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['Pending', 'Processing', 'Completed', 'Cancelled']:
            return jsonify({"message": "Invalid status"}), 400

        order = Order.query.get(order_id)

        if not order:
            return jsonify({"message": "Order not found"}), 404

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

# Seller cek Order
@jwt_required()
def seller_get_orders():
    """
    Seller melihat pesanan yang berisi produk mereka.
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_seller:
            return jsonify({"message": "Only sellers can view their orders"}), 403

        # Cari produk yang dijual oleh seller
        products = Product.query.filter_by(seller_id=user_id).all()
        product_ids = [product.id for product in products]

        # Cari pesanan yang berisi produk tersebut
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

    except SQLAlchemyError as e:
        return jsonify({"message": "Error retrieving seller orders", "error": str(e)}), 500