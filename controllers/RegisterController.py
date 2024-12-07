import random
from flask import current_app, jsonify, request
from connectors.db import db # Import database connector
from models.otp import OTP # Model OTP untuk database
from models.user import User  # Model User untuk database
from flask_mail import Message
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


# Generate OTP
def generate_otp():
    """Generate a random 6-digit OTP."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

# Fungsi untuk mengirim email OTP
def send_otp_email(email, otp_code, subject="Your Registration OTP"):
    """Send OTP email."""
    try:
        msg = Message(
            subject=subject,
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=[email],
            body=f"Your OTP is: {otp_code}. It will expire in 5 minutes."
        )
        current_app.extensions['mail'].send(msg)
        return True, "OTP sent successfully"
    except Exception as e:
        current_app.logger.error(f"Failed to send OTP email: {e}")
        return False, f"Failed to send email: {e}"

# Step 1: Register user and send OTP
def register_user():
    data = request.get_json()
    
    # Validasi input
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')

    if not all([first_name, last_name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    # Cek apakah email sudah terdaftar
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email is already registered"}), 400

    # Hapus OTP lama dan buat OTP baru
    OTP.query.filter_by(email=email).delete()
    otp_code = generate_otp()
    new_otp = OTP(
        email=email,
        otp_code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.session.add(new_otp)
    db.session.commit()

    # Kirim OTP
    success, message = send_otp_email(email, otp_code)
    if not success:
        return jsonify({"error": message}), 500

    return jsonify({"message": message}), 200

# Step 2: Verify OTP and complete registration
def verify_otp():
    """Handle OTP verification."""
    try:
        # Hapus OTP yang sudah kedaluwarsa
        OTP.query.filter(OTP.expires_at < datetime.utcnow()).delete()
        db.session.commit()

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        email = data.get('email')
        otp_code = data.get('otp')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        # Validasi input
        if not all([email, otp_code, password, first_name, last_name]):
            return jsonify({"error": "All fields are required"}), 400

       # Fetch OTP entry
        otp_entry = OTP.query.filter_by(email=email, otp_code=otp_code).first()
        if not otp_entry:
            return jsonify({"error": "Invalid OTP"}), 400

        # Periksa apakah OTP sudah kedaluwarsa
        if otp_entry.expires_at < datetime.utcnow():
            db.session.delete(otp_entry)  # Hapus OTP kedaluwarsa
            db.session.commit()
            return jsonify({"error": "OTP has expired"}), 400

        # Cek apakah pengguna sudah ada
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # Buat pengguna baru
        new_user = User(
            email=email,
            password=generate_password_hash(password),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        db.session.add(new_user)
        db.session.delete(otp_entry)  # Hapus OTP yang sudah diverifikasi
        db.session.commit()

        return jsonify({"message": "Registration completed successfully"}), 201
    except Exception as e:
        current_app.logger.error(f"Error: {e}")  # Log error yang terjadi
        db.session.rollback()  # Rollback jika ada error
        return jsonify({"error": f"An error occurred: {e}"}), 500

# Resend OTP
def resend_otp():
    """Handle Resend OTP."""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Hapus OTP lama dan buat OTP baru
        OTP.query.filter_by(email=email).delete()
        otp_code = generate_otp()
        new_otp = OTP(
            email=email,
            otp_code=otp_code,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        db.session.add(new_otp)
        db.session.commit()

        # Kirim OTP baru
        success, message = send_otp_email(email, otp_code, subject="Your New Registration OTP")
        if not success:
            return jsonify({"error": message}), 500

        return jsonify({"message": message}), 200
    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {e}"}), 500