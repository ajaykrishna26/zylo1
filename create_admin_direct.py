#!/usr/bin/env python3
import sys
from pathlib import Path
import os

# Ensure we're in the right directory for imports
os.chdir(r'C:\Users\DELL\OneDrive\Pictures\Desktop\reading_assistant-ak\reading_assistant-ak')
ROOT = Path(os.getcwd())
sys.path.insert(0, str(ROOT))

print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

try:
    from BACKEND.db import get_users_collection
    import bcrypt
    
    print("[1] Connecting to MongoDB...")
    users = get_users_collection()
    print("[OK] Connected to users collection")
    
    email = 'admin@gmail.com'
    password = 'Admin@123'
    name = 'Admin'
    
    print(f"\n[2] Checking if admin exists: {email}")
    existing = users.find_one({'email': email.lower()})
    
    if existing:
        print(f"[OK] Admin user {email} already exists!")
        print(f"     ID: {existing.get('_id')}")
    else:
        print(f"[*] Admin not found, creating...")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_doc = {
            'email': email.lower(),
            'password_hash': password_hash,
            'name': name,
            'created_at': __import__('datetime').datetime.utcnow(),
            'updated_at': __import__('datetime').datetime.utcnow()
        }
        
        result = users.insert_one(user_doc)
        print(f'[OK] Admin account created successfully!')
        print(f'     Email: {email}')
        print(f'     Password: {password}')
        print(f'     User ID: {result.inserted_id}')
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
