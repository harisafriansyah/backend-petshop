from connectors.db import db
from datetime import datetime

class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)  # ID pengguna
    product_id = db.Column(db.Integer, nullable=False)  # ID produk
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Tanggal ditambahkan
