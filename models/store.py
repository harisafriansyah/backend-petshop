from connectors.db import db
from datetime import datetime

class Store(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nama_toko = db.Column(db.String(100), nullable=False)
    alamat_toko = db.Column(db.String(200), nullable=False)
    no_tlp = db.Column(db.String(15), nullable=False)
    bank = db.Column(db.String(200), nullable=False)
    no_rek = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, user_id, nama_toko, alamat_toko, no_tlp, bank, no_rek):
        self.user_id = user_id
        self.nama_toko = nama_toko
        self.alamat_toko = alamat_toko
        self.no_tlp = no_tlp
        self.bank = bank
        self.no_rek = no_rek

    def __repr__(self):
        return f"<Store {self.nama_toko}>"
