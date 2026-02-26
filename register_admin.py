import requests
import json

BASE_URL = "http://localhost:5000"

# Register admin account via API
print("[*] Creating admin account via API...")
print(f"    Email: admin@gmail.com")
print(f"    Password: Admin@123\n")

response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "name": "Admin",
        "email": "admin@gmail.com",
        "password": "Admin@123"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 201:
    print("\n[OK] Admin account created successfully!")
    print("\n--- Login Credentials ---")
    print("Email: admin@gmail.com")
    print("Password: Admin@123")
    print("---\n")
    print("You can now log in at http://localhost:3002")
elif response.status_code == 409:
    print("\n[OK] Admin account already exists!")
    print("\n--- Login Credentials ---")
    print("Email: admin@gmail.com")
    print("Password: Admin@123")
    print("---\n")
    print("You can now log in at http://localhost:3002")
else:
    print(f"\n[ERROR] Failed to create admin: {response.json()}")
