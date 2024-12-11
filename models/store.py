from connectors.db import db
from datetime import datetime

class Store(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nama_toko = db.Column(db.String(100), nullable=False)
    nama_domain = db.Column(db.String(100), unique=True, nullable=False)
    alamat_lengkap = db.Column(db.Text, nullable=False)
    deskripsi_toko = db.Column(db.Text, nullable=True)

     # Default status langsung aktif
    status = db.Column(db.String(20), default="active", nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    owner = db.relationship('User', back_populates='stores')

    def __repr__(self):
        return f"<Store {self.nama_toko} (status={self.status})>"
