from datetime import datetime, timedelta, timezone
import jwt
import json

# Konfigurasi
SECRET_KEY = "c9ffcb3976c988fbb9f4d01b96710799003c80667cefa021c1bb8d3d8ba8db76"

# Membuat token
payload = {
    "exp": datetime.now(timezone.utc) + timedelta(minutes=15),  # Menggunakan timezone-aware datetime
    "iat": datetime.now(timezone.utc),  # Menggunakan timezone-aware datetime
    "sub": json.dumps({"id": 11, "email": "example@example.com"})  # Konversi sub menjadi string
}

try:
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    print("Generated token:", token)

    # Mendekode token
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    decoded["sub"] = json.loads(decoded["sub"])  # Kembalikan ke dictionary
    print("Decoded payload:", decoded)
except jwt.InvalidTokenError as e:
    print(f"Invalid token: {str(e)}")
