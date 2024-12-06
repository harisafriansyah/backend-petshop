from connectors.db import db
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime

class User(db.Model):
    _tablename_ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    foto_profil = db.Column(db.String(255), nullable=True)  # Path to the profile picture
    alamat = db.Column(db.String(255), nullable=True)
    no_tlp = db.Column(db.Integer, nullable=True)
    bank = db.Column(db.String(100), nullable=True)
    no_rek = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def _init_(self, nama, email, username, password, foto_profil=None, alamat=None, no_tlp=None, bank=None, no_rek=None):
        self.nama = nama
        self.email = email
        self.username = username
        self.password = password
        self.foto_profil = foto_profil
        self.alamat = alamat
        self.no_tlp = no_tlp
        self.bank = bank
        self.no_rek = no_rek

    def _repr_(self):
        return f'<User {self.username}>'