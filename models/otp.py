from connectors.db import db
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime, timedelta

class OTP(db.Model):
    __tablename__ = 'otp'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, otp_code):
        self.email = email
        self.otp_code = otp_code
        self.expires_at = datetime.utcnow() + timedelta(minutes=5)