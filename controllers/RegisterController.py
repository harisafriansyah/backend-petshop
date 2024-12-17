import random
from flask import current_app, jsonify, request
from connectors.db import db # Import database connector
from models.otp import OTP # Model OTP untuk database
from models.user import User  # Model User untuk database
from flask_mail import Message
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Cooldown time in seconds
COOLDOWN_TIME = 60

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

# Utility: Clear expired OTPs
def clear_expired_otps():
    """Remove expired OTPs from the database."""
    OTP.query.filter(OTP.expires_at < datetime.utcnow()).delete()
    db.session.commit()
    current_app.logger.info("Expired OTPs cleared.")

# Utility: Save OTP
def save_new_otp(email, user_data=None):
    """Delete existing OTP and save a new one."""
    OTP.query.filter_by(email=email).delete()
    otp_code = generate_otp()
    new_otp = OTP(
        email=email,
        otp_code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        user_data=user_data  # Save user details temporarily with the OTP
    )
    db.session.add(new_otp)
    db.session.commit()
    return otp_code


# Check OTP Cooldown
def is_otp_in_cooldown(email):
    """Check OTP cooldown status."""
    otp_entry = OTP.query.filter_by(email=email).first()
    if otp_entry:
        time_since_creation = (datetime.utcnow() - otp_entry.created_at).total_seconds()
        if time_since_creation < COOLDOWN_TIME:
            return True, int(COOLDOWN_TIME - time_since_creation)
    return False, 0    

# Validate input data
def validate_data(data, required_fields):
    """Validate if all required fields are present."""
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    return True, None    

# Endpoints
# Step 1: Register user and send OTP
def register_user():
    """Handle user registration and send OTP."""
    data = request.get_json()

    # Validate input
    valid, message = validate_data(data, ['first_name', 'last_name', 'email', 'password'])
    if not valid:
        return jsonify({"status": "error", "message": message}), 400

    # Check if email is already registered
    email = data.get('email')
    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email is already registered"}), 400

    # Create user_data object to store temporarily
    user_data = {
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "email": data['email'],
        "password": data['password']
    }

    # Generate & send OTP
    otp_code = save_new_otp(email, user_data)  # Pass user_data explicitly
    success, message = send_otp_email(email, otp_code)
    if not success:
        return jsonify({"status": "error", "message": message}), 500

    return jsonify({"status": "success", "message": "OTP sent successfully"}), 200


# Step 2: Verify OTP and complete registration
def verify_otp():
    """
    Handle OTP verification. Complete user registration after OTP is verified.
    """
    try:
        # Hapus OTP yang sudah kedaluwarsa
        clear_expired_otps()

        # Ambil data dari request
        data = request.get_json()
        valid, message = validate_data(data, ['otp'])
        if not valid:
            return jsonify({"status": "error", "message": message}), 400

        # Cari OTP di database
        otp_code = data.get('otp')
        otp_entry = OTP.query.filter_by(otp_code=otp_code).first()

        # Validasi OTP
        if not otp_entry or not otp_entry.is_valid():
            current_app.logger.warning(f"Invalid or expired OTP attempt: {otp_code}")
            return jsonify({"status": "error", "message": "Invalid or expired OTP"}), 400

        # Ambil email dan user_data dari OTP
        email = otp_entry.email
        user_data = otp_entry.user_data  # Ambil data sementara

        if not user_data:
            return jsonify({"status": "error", "message": "User data is missing"}), 500

        # Cek apakah pengguna sudah ada
        if User.query.filter_by(email=email).first():
            return jsonify({"status": "error", "message": "User already exists"}), 400

        # Buat pengguna baru
        new_user = User(
            email=email,
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        # Set hashed password
        new_user.set_password(user_data['password'])

        # Simpan pengguna ke database
        db.session.add(new_user)
        db.session.delete(otp_entry)  # Hapus OTP yang sudah diverifikasi
        db.session.commit()

        # Log sukses
        current_app.logger.info(f"User {email} registered successfully.")
        return jsonify({"status": "success", "message": "Registration completed successfully"}), 201

    except Exception as e:
        current_app.logger.error(f"Error during OTP verification: {e}")
        db.session.rollback()
        return jsonify({"status": "error", "message": "An error occurred during registration"}), 500

# Resend OTP with cooldown check
def resend_otp():
    """Handle Resend OTP with cooldown."""
    data = request.get_json()
    valid, message = validate_data(data, ['email'])
    if not valid:
        return jsonify({"status": "error", "message": message}), 400

    email = data.get('email')

    # Check for OTP cooldown
    otp_entry = OTP.query.filter_by(email=email).first()
    if otp_entry:
        in_cooldown, remaining_time = is_otp_in_cooldown(email)
        if in_cooldown:
            return jsonify({
                "status": "error",
                "message": f"Please wait {remaining_time} seconds before requesting a new OTP"
            }), 429

    # Fetch user data temporarily
    user_data = otp_entry.user_data if otp_entry else None
    if not user_data:
        return jsonify({"status": "error", "message": "User data not found for resending OTP"}), 400

    # Generate and send new OTP
    otp_code = save_new_otp(email)
    success, message = send_otp_email(email, otp_code, subject="Your New Registration OTP")
    if not success:
        return jsonify({"status": "error", "message": message}), 500

    return jsonify({"status": "success", "message": message}), 200
