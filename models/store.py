from connectors.db import db
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime

class Store(db.Model):
    _tablename_ = 'stores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    penjual_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    nama_toko = db.Column(db.String(100), nullable=False)
    alamat_toko = db.Column(db.String(200), nullable=False)
    no_telp = db.Column(db.Integer, nullable=False)
    bank = db.Column(db.String(200), nullable=False)
    no_rek = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def _init_(self, nama_toko, alamat_toko, no_telp, bank, no_rek):
        self.nama_toko = nama_toko
        self.alamat_toko = alamat_toko
        self.no_telp = no_telp
        self.bank = bank
        self.no_rek = no_rek
    
    user = db.relationship("User", backref="stores")

    
    def _repr_(self):
        return f'<Store {self.nama_toko}>'