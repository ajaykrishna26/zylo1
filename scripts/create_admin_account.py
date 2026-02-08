import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from BACKEND.db import get_users_collection
import bcrypt

if __name__ == '__main__':
    email = 'admin@example.com'
    password = 'Admin123!@'
    name = 'Admin'
    
    users = get_users_collection()
    
    # Check if user already exists
    existing = users.find_one({'email': email.lower()})
    if existing:
        print(f'Admin user {email} already exists')
        sys.exit(0)
    
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
    print(f'Admin account created successfully!')
    print(f'Email: {email}')
    print(f'Password: {password}')
    print(f'User ID: {result.inserted_id}')
