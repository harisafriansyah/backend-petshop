from flask import Flask
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp

def register_routes(app: Flask):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
