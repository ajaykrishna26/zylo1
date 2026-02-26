#!/usr/bin/env python3
"""
Direct admin account creation - run from repo root
"""
import sys
import os

# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add backend to path
sys.path.insert(0, os.getcwd())

from BACKEND.db import get_users_collection
import bcrypt
from datetime import datetime

def create_admin():
    email = 'admin@gmail.com'
    password = 'Admin@123'
    name = 'Admin'
    
    try:
        print("[1] Connecting to MongoDB...")
        users = get_users_collection()
        print("    [OK] Connected")
        
        # Check if exists
        print(f"\n[2] Checking if {email} exists...")
        existing = users.find_one({'email': email.lower()})
        
        if existing:
            print(f"    [OK] Admin already exists!")
            print(f"         Email: {existing['email']}")
            return True
        
        # Create new admin
        print(f"    [*] Not found. Creating new admin...")
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_doc = {
            'email': email.lower(),
            'password_hash': password_hash,
            'name': name,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = users.insert_one(user_doc)
        print(f"\n[OK] Admin created successfully!")
        print(f"     Email: {email}")
        print(f"     Password: {password}")
        print(f"     ID: {result.inserted_id}")
        print(f"\nYou can now log in with these credentials!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to create admin: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_admin()
    sys.exit(0 if success else 1)
