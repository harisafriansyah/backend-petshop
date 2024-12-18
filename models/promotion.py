from connectors.db import db
from datetime import datetime

class Promotion(db.Model):
    __tablename__ = 'promotions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    promotion_name = db.Column(db.String(255), nullable=False)
    promotion_period_start = db.Column(db.DateTime, nullable=False)
    promotion_period_end = db.Column(db.DateTime, nullable=False)
    max_quantity = db.Column(db.Integer, nullable=False)
    discount_percent = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="active")  # 'active', 'expired', 'upcoming'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Product (One-to-Many)
    product = db.relationship('Product', back_populates='promotions', lazy=True)

    # Index for optimizing queries
    __table_args__ = (
        db.Index('idx_promotion_period', 'promotion_period_start', 'promotion_period_end'),
        db.UniqueConstraint('product_id', 'promotion_period_start', name='uq_product_promotion'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate the promotion data during initialization
        if self.promotion_period_start >= self.promotion_period_end:
            raise ValueError("Promotion start date must be before end date")
        if self.discount_percent <= 0 or self.discount_percent > 100:
            raise ValueError("Discount percentage must be between 0 and 100")

    def is_active(self):
        """
        Check if the promotion is currently active.
        """
        now = datetime.utcnow()
        return (
            self.promotion_period_start <= now <= self.promotion_period_end and
            self.promotion_period_start < self.promotion_period_end
        )

    def update_status(self):
        """
        Update the promotion status based on the current date.
        """
        now = datetime.utcnow()
        if now < self.promotion_period_start:
            self.status = "upcoming"
        elif now > self.promotion_period_end:
            self.status = "expired"
        else:
            self.status = "active"

    def apply_discount(self, price):
        """
        Apply the discount to a given price.
        """
        if self.is_active():
            return round(price * (1 - self.discount_percent / 100), 2)
        return price

    def can_apply_promotion(self, current_usage):
        """
        Check if the promotion can still be applied based on max_quantity.
        """
        return current_usage < self.max_quantity

    def discounted_price(self):
        """
        Calculate and return the discounted price for the associated product.
        """
        return self.apply_discount(self.product.price) if self.product else None

    def to_dict(self):
        """
        Convert promotion data to a dictionary for JSON responses.
        """
        promotion_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        promotion_dict["is_active"] = self.is_active()
        return promotion_dict
