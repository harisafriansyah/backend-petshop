from connectors.db import db
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime, timedelta

class OTP(db.Model):
    __tablename__ = 'otp'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, otp_code, expires_at):
        self.email = email
        self.otp_code = otp_code
        self.expires_at = expires_at

    def is_valid(self):
        return self.expires_at > datetime.utcnow()