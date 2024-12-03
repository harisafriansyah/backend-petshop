from flask import Flask
from connectors.config import Config
from models.user import db

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Menggunakan konfigurasi dari config.py
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return {"message": "Welcome to Flask!"}

if __name__ == "_main_":
    app.run(debug=True)