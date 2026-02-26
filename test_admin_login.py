import requests
import json

# Test login with the new admin credentials
url = 'http://localhost:5000/api/auth/login'
payload = {
    'email': 'admin@gmail.com',
    'password': 'Admin@123'
}

try:
    r = requests.post(url, json=payload, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    if r.status_code == 200:
        result = r.json()
        print(f"\n✓ SUCCESS!")
        print(f"  User: {result.get('user', {}).get('name')}")
        print(f"  Email: {result.get('user', {}).get('email')}")
        print(f"  Token: {result.get('access_token', 'N/A')[:50]}...")
    elif r.status_code == 401:
        print(f"\n✗ Login failed - Invalid credentials")
        print(f"  Admin account may not exist yet")
        print(f"\n  Run this to create the admin:")
        print(f"  python scripts/create_admin_account.py")
    else:
        print(f"\n✗ Server error: {r.status_code}")
except Exception as e:
    print(f"ERROR: {e}")
    print("\nMake sure backend is running on http://localhost:5000")
