from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from connectors.config import Config
from connectors.db import db, jwt  # Connector database
from flask_mail import Mail  # Mail untuk pengiriman OTP
from routes import register_all_routes  # Import fungsi untuk mendaftarkan semua routes

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
    jwt.init_app(app)

    # Inisialisasi Flask-Migrate
    migrate = Migrate(app, db)

    # Inisialisasi CORS untuk publik (semua origin bisa akses API)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://localhost:3000", "https://frontend-production-url.com"]}})

    # Register semua routes dari folder routes
    register_all_routes(app)

    # Cek koneksi database
    Config.check_database(app)

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