#!/usr/bin/env python3
import bcrypt
from pymongo import MongoClient
from datetime import datetime

# Hash the password
pwd_hash = bcrypt.hashpw(b'Admin@123', bcrypt.gensalt())

# Connect and insert
client = MongoClient('mongodb://localhost:27017/dyslexia_assistant')
db = client['dyslexia_assistant']
users = db['users']

# Remove old admin if exists
users.delete_many({'email': 'admin@gmail.com'})

# Insert new admin
result = users.insert_one({
    'name': 'Admin',
    'email': 'admin@gmail.com',
    'password_hash': pwd_hash,
    'created_at': datetime.utcnow(),
    'updated_at': datetime.utcnow()
})

print(f"✓ Admin created with ID: {result.inserted_id}")
print(f"  Email: admin@gmail.com")
print(f"  Password: Admin@123")

client.close()
