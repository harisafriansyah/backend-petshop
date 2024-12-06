import random
from flask import current_app, jsonify, request
from connectors.db import db # Import database connector
from models.otp import OTP # Model OTP untuk database
from models.user import User  # Model User untuk database
from flask_mail import Message
from datetime import datetime

def generate_otp():
    """Generate a random 6-digit OTP."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp():
    """Handle OTP sending for user registration."""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Generate OTP
    otp_code = generate_otp()

    # Check if OTP already exists for this email
    existing_otp = OTP.query.filter_by(email=email).first()
    if existing_otp:
        db.session.delete(existing_otp)  # Delete the old OTP
        db.session.commit()

    # Save OTP to the database
    new_otp = OTP(email=email, otp_code=otp_code)
    db.session.add(new_otp)
    db.session.commit()

    # Send OTP via email
    try:
        msg = Message(
            subject="Your Registration OTP",
            sender=current_app.config["MAIL_DEFAULT_SENDER"],  # Ambil sender dari konfigurasi
            recipients=[email],
            body=f"Your OTP for registration is: {otp_code}. This OTP will expire in 5 minutes."
        )
        current_app.extensions['mail'].send(msg)  # Gunakan current_app untuk mengakses mail instance
        return jsonify({"message": "OTP sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {e}"}), 500

# Verifikasi OTP
def verify_otp():
    """Handle OTP verification."""
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    # Cari OTP berdasarkan email dan kode OTP
    otp_entry = OTP.query.filter_by(email=email, otp_code=otp).first()

    if not otp_entry:
        return jsonify({"error": "Invalid OTP"}), 400

    # Periksa apakah OTP sudah kedaluwarsa
    if otp_entry.expires_at < datetime.utcnow():
        return jsonify({"error": "OTP has expired"}), 400

    # Jika OTP valid, hapus entry OTP dari database
    db.session.delete(otp_entry)
    db.session.commit()

    return jsonify({"message": "OTP verified successfully"}), 200