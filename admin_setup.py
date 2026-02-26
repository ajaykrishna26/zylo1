#!/usr/bin/env python3
"""
ADMIN ACCOUNT SETUP TOOL
Double-click this file or run: python admin_setup.py
"""

import sys
import os

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

print("=" * 60)
print("ADMIN ACCOUNT SETUP")
print("=" * 60)

# Try to import dependencies
try:
    import bcrypt
    from datetime import datetime
    from pymongo import MongoClient
except ImportError as e:
    print(f"\n[ERROR] Missing dependency: {e}")
    print("\nInstall with: pip install pymongo bcrypt")
    input("\nPress Enter to exit...")
    sys.exit(1)

# MongoDB connection
try:
    print("\n[1] Connecting to MongoDB...")
    print("    URI: mongodb://localhost:27017/dyslexia_assistant")
    
    client = MongoClient('mongodb://localhost:27017/dyslexia_assistant', serverSelectionTimeoutMS=5000)
    client.server_info()
    
    db = client['dyslexia_assistant']
    users_col = db['users']
    
    print("    [OK] Connected!")
    
except Exception as e:
    print(f"    [ERROR] Could not connect to MongoDB!")
    print(f"    Message: {e}")
    print("\n    Make sure:")
    print("    - MongoDB is running")
    print("    - Connection string is correct")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Admin credentials
email = 'admin@gmail.com'
password = 'Admin@123'

print(f"\n[2] Setting up admin account:")
print(f"    Email: {email}")
print(f"    Password: {password}")

try:
    # Check if exists
    existing = users_col.find_one({'email': email.lower()})
    
    if existing:
        print(f"\n    [OK] Admin account already exists!")
        print(f"         ID: {existing.get('_id')}")
        print(f"\n    You can now log in with:")
        print(f"    - Email: {email}")
        print(f"    - Password: {password}")
    else:
        print(f"\n    [*] Account not found, creating...")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create admin doc
        admin_doc = {
            'name': 'Admin',
            'email': email.lower(),
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert
        result = users_col.insert_one(admin_doc)
        
        print(f"    [OK] Admin account created successfully!")
        print(f"         ID: {result.inserted_id}")
        print(f"\n    You can now log in with:")
        print(f"    - Email: {email}")
        print(f"    - Password: {password}")
    
    # Verify login works
    print(f"\n[3] Verifying login...")
    import requests
    
    try:
        r = requests.post('http://localhost:5000/api/auth/login', 
            json={'email': email, 'password': password},
            timeout=5
        )
        
        if r.status_code == 200:
            print(f"    [OK] Login verified! ✓")
            print(f"\n✓ Admin setup complete! You're ready to log in.")
            print(f"\n  Go to: http://localhost:3002")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
        elif r.status_code == 401:
            print(f"    [WARN] Account exists but login failed (401)")
            print(f"         Check credentials or password hash")
        else:
            print(f"    [WARN] Login test returned: {r.status_code}")
    
    except requests.exceptions.ConnectionError:
        print(f"    [WARN] Backend not running at http://localhost:5000")
        print(f"         Start backend first: python BACKEND/app.py")
    except Exception as e:
        print(f"    [WARN] Could not verify login: {e}")
    
    client.close()
    print(f"\nDone! Press Enter to exit.")
    input()

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)
