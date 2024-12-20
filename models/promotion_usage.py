from connectors.db import db
from datetime import datetime

class UserPromotionUsage(db.Model):
    __tablename__ = 'user_promotion_usage'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotions.id'), nullable=False)
    quantity_used = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Promotion
    promotion = db.relationship('Promotion', backref='user_usages')
