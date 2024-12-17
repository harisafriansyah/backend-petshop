import os
import psycopg2
from datetime import timedelta
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.getenv('SQLALCHEMY_POOL_SIZE', 10)),  # Default 10 connections
        "max_overflow": int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 5)),  # Extra connections if pool full
        "pool_timeout": int(os.getenv('SQLALCHEMY_POOL_TIMEOUT', 30)),  # Timeout in seconds
        "pool_recycle": int(os.getenv('SQLALCHEMY_POOL_RECYCLE', 1800)),  # Recycle every 30 minutes
    }


    # Email configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # Flask secret key
    SECRET_KEY = os.getenv('SECRET_KEY')  # Ensure this is set securely in .env

    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Ensure this is set securely in .env
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 15)))  # Default 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 7)))  # Default 7 days

    # Token location configuration
    JWT_TOKEN_LOCATION = os.getenv('JWT_TOKEN_LOCATION', 'headers').split(',')  # Options: 'headers', 'cookies', 'query_string', 'json'

    # Optional: Cookie configuration (if using cookies for tokens)
    JWT_COOKIE_SECURE = os.getenv('JWT_COOKIE_SECURE', 'False').lower() == 'true'  # Set to True in production
    JWT_ACCESS_COOKIE_PATH = os.getenv('JWT_ACCESS_COOKIE_PATH', '/')
    JWT_REFRESH_COOKIE_PATH = os.getenv('JWT_REFRESH_COOKIE_PATH', '/auth/refresh-token')

    # Optional: Enable token blacklisting
    JWT_BLACKLIST_ENABLED = os.getenv('JWT_BLACKLIST_ENABLED', 'True').lower() == 'true'
    JWT_BLACKLIST_TOKEN_CHECKS = os.getenv('JWT_BLACKLIST_TOKEN_CHECKS', 'access,refresh').split(',')

    # Token header name configuration
    JWT_HEADER_NAME = os.getenv('JWT_HEADER_NAME', 'Authorization')  # Default is 'Authorization'
    JWT_HEADER_TYPE = os.getenv('JWT_HEADER_TYPE', 'Bearer')  # Default is 'Bearer'

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )

    @staticmethod
    def check_database(app):
        """Cek koneksi database dengan app context."""
        try:
            from connectors.db import db
            from sqlalchemy import text
            with app.app_context():
                with db.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
            print("Database connection successful!")
        except Exception as e:
            print(f"Database connection failed: {e}")