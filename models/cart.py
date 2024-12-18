from connectors.db import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Relasi dengan tabel users
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Relasi dengan tabel products
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi dengan tabel Product
    product = db.relationship('Product', back_populates='carts', lazy=True)

    def __repr__(self):
        return f"<Cart {self.id} - Product {self.product_id}>"
