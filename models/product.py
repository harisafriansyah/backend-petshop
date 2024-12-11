from connectors.db import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    nama_produk = db.Column(db.String(255), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    harga = db.Column(db.Float, nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    gambar = db.Column(db.String(255), nullable=True)
    kategori = db.Column(db.String(50), nullable=False)
    jenis_hewan = db.Column(db.String(50), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    store = db.relationship("Store", backref="products")

    def __repr__(self):
        return f"<Product {self.nama_produk}>"
