from flask import Flask
from flask_migrate import Migrate
from connectors.config import Config
from connectors.db import db  # Connector database
from flask_mail import Mail  # Mail untuk pengiriman OTP
from routes import register_routes  # Import fungsi untuk mendaftarkan semua routes

# Inisialisasi Flask dan Flask-Mail
mail = Mail()

def create_app():
    """Factory function untuk membuat instance aplikasi Flask."""
    app = Flask(__name__)

    # Menggunakan konfigurasi dari config.py
    app.config.from_object(Config)
    
    # Inisialisasi ekstensi
    db.init_app(app)
    mail.init_app(app)

    # Inisialisasi Flask-Migrate
    migrate = Migrate(app, db)

    # Register semua routes dari folder routes
    register_routes(app)

    # Inisialisasi tabel database jika diperlukan
    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return {"message": "Welcome to Flask!"}

    return app

if __name__ == "__main__":
    # Jalankan aplikasi
    app = create_app()
    app.run(debug=True)