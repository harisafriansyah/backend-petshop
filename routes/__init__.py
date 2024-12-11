from flask import Flask
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.seller_routes import seller_bp

def register_all_routes(app: Flask):
    """
    Register all blueprint routes for the application.
    :param app: Flask application instance
    """
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(seller_bp, url_prefix='/seller')
