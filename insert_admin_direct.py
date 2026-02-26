#!/usr/bin/env python3
"""
Direct MongoDB admin insertion
Run from: python insert_admin_direct.py
"""
import bcrypt
from datetime import datetime
from pymongo import MongoClient
import os

# Connect to MongoDB
try:
    URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/dyslexia_assistant')
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    
    db = client['dyslexia_assistant']
    users_col = db['users']
    
    print("[1] Connected to MongoDB")
    
    # Admin credentials
    email = 'admin@gmail.com'
    password = 'Admin@123'
    
    # Check if exists
    existing = users_col.find_one({'email': email.lower()})
    if existing:
        print(f"[OK] Admin already exists!")
        print(f"     Email: {existing['email']}")
    else:
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert admin
        admin_doc = {
            'name': 'Admin',
            'email': email.lower(),
            'password_hash': password_hash,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = users_col.insert_one(admin_doc)
        print(f"[OK] Admin created!")
        print(f"     Email: {email}")
        print(f"     Password: {password}")
        print(f"     ID: {result.inserted_id}")
        
    client.close()
    print("\n✓ Disconnected from MongoDB")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
