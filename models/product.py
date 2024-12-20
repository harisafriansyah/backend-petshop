from connectors.db import db
from datetime import datetime
from models.product_image import ProductImage


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    nama_produk = db.Column(db.String(255), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    harga = db.Column(db.Float, nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    kategori = db.Column(db.String(50), nullable=False, index=True)
    jenis_hewan = db.Column(db.String(50), nullable=False, index=True)
    berat = db.Column(db.Float, nullable=False)  # Wajib diisi
    panjang = db.Column(db.Float, nullable=True, default=0.0)
    lebar = db.Column(db.Float, nullable=True, default=0.0)
    tinggi = db.Column(db.Float, nullable=True, default=0.0)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relasi ke tabel Store
    store = db.relationship("Store", backref="products")

    # Relasi ke tabel ProductImage
    images = db.relationship(
        'ProductImage',
        back_populates='product',
        cascade='all, delete-orphan'
    )

    # Relasi Promotion
    promotions = db.relationship(
        'Promotion', 
        back_populates="product", 
        cascade="all, delete-orphan", 
        lazy='joined'  # Menggunakan string untuk opsi lazy loading
    )
    
    # Relationship to Cart (newly added)
    carts = db.relationship('Cart', back_populates='product', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Product {self.nama_produk}>"

    def validate(self):
        if self.harga <= 0:
            raise ValueError("Harga must be greater than 0")
        if self.stok < 0:
            raise ValueError("Stok cannot be negative")

    def get_images(self):
        return [img.image_url for img in self.images]

    def to_dict(self):
        # Ambil promosi aktif terbaru (opsional: bisa diubah sesuai kebutuhan)
        latest_promotion = (
            Promotion.query.filter_by(product_id=self.id)
            .order_by(Promotion.id.desc())
            .first()
        )

        return {
            "id": self.id,
            "nama_produk": self.nama_produk,
            "harga": self.harga,
            "stok": self.stok,
            "kategori": self.kategori,
            "jenis_hewan": self.jenis_hewan,
            "berat": self.berat,
            "ukuran": {
                "panjang": self.panjang,
                "lebar": self.lebar,
                "tinggi": self.tinggi,
            },
            "images": self.get_images(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "promotion": latest_promotion.to_dict() if latest_promotion else None,  # Sertakan data promosi jika ada
        }


