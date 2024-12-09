import secrets

# Generate a secure secret key
secure_key = secrets.token_hex(32)
print(f"Generated SECRET_KEY: {secure_key}")
