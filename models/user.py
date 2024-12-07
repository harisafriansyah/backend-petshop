from connectors.db import db
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    # Primary Fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    foto_profil = db.Column(db.String(255), nullable=True)
    no_tlp = db.Column(db.String(15), nullable=True)  
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relasi
    addresses = db.relationship("Address", backref="user", lazy=True, cascade="all, delete-orphan")
    banks = db.relationship("Bank", backref="user", lazy=True, cascade="all, delete-orphan")
    stores = db.relationship("Store", backref="owner", lazy=True, cascade="all, delete-orphan")

    # Constructor
    def __init__(self, email, password, first_name, last_name, no_tlp=None, foto_profil=None):
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.no_tlp = no_tlp
        self.foto_profil = foto_profil

    def __init__(self, email, first_name, last_name):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
