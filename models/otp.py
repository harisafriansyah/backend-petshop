from connectors.db import db
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime

class OTP(db.Model):
    __tablename__ = 'otp'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    otp_code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    user_data = db.Column(JSON, nullable=True)  # Store temporary user details

    def __init__(self, email, otp_code, expires_at, user_data=None):
        """
        Constructor for OTP model.
        :param email: User's email
        :param otp_code: OTP code
        :param expires_at: Expiration time for the OTP
        :param user_data: Temporary user data (optional)
        """
        self.email = email
        self.otp_code = otp_code
        self.expires_at = expires_at
        self.user_data = user_data  # Assign user_data if provided

    def is_valid(self):
        """Check if the OTP is still valid."""
        return self.expires_at > datetime.utcnow()
