import os

# Database configuration
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://GFPTimF_studyingat:5e58b60f59d94e8745e17730d6ec4e408530d824@a5nm0.h.filess.io:3307/GFPTimF_studyingat')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'tim3berlinfinalproject@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'esxmsmbfkgmtabpt')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'tim3berlinfinalproject@gmail.com')

# Flask secret key
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')