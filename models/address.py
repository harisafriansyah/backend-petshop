from connectors.db import db
from datetime import datetime

class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nama_penerima = db.Column(db.String(100), nullable=False)
    no_tlp = db.Column(db.String(15), nullable=True)
    label = db.Column(db.String(100), nullable=False)
    kota = db.Column(db.String(100), nullable=False)
    kelurahan = db.Column(db.String(100), nullable=False)
    kecamatan = db.Column(db.String(100), nullable=False)
    provinsi = db.Column(db.String(100), nullable=False)
    kode_pos = db.Column(db.String(10), nullable=False)
    alamat = db.Column(db.String(255), nullable=False)
    catatan_kurir = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow, nullable=True)

    def __init__(self, user_id, nama_penerima, no_tlp, label, kota, kelurahan, kecamatan, provinsi, kode_pos, alamat, catatan_kurir=None):
        self.user_id = user_id
        self.nama_penerima = nama_penerima
        self.no_tlp = no_tlp
        self.label = label
        self.kota = kota
        self.kelurahan = kelurahan
        self.kecamatan = kecamatan
        self.provinsi = provinsi
        self.kode_pos = kode_pos
        self.alamat = alamat
        self.catatan_kurir = catatan_kurir
