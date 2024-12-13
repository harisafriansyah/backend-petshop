from flask import Flask
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.seller_routes import seller_bp
from routes.product_routes import product_bp
from routes.file_upload_routes import file_upload_bp

def register_all_routes(app: Flask):
    """
    Register all blueprint routes for the application.
    :param app: Flask application instance
    """
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(seller_bp, url_prefix='/seller')
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(file_upload_bp, url_prefix='/files')