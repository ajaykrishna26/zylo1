️#!/usr/bin/env python3
"""
COMPREHENSIVE TROUBLESHOOTING GUIDE
Run this to fix all common admin setup errors
"""
import subprocess
import sys
import os
import time

def run_cmd(cmd, description):
    """Run a command and return status"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_backend():
    """Check if backend is running"""
    try:
        import requests
        r = requests.get('http://localhost:5000/api/health', timeout=2)
        return r.status_code == 200
    except:
        return False

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        return True
    except:
        return False

def check_frontend():
    """Check if frontend is running"""
    try:
        import requests
        r = requests.get('http://localhost:3002', timeout=2)
        return r.status_code >= 200
    except:
        return False

print("="*70)
print("ZYLO TROUBLESHOOTING GUIDE")
print("="*70)

print("\n[1] CHECKING SERVICES...")
print("-" * 70)

backend_ok = check_backend()
print(f"  Backend (localhost:5000):  {'✓ RUNNING' if backend_ok else '✗ NOT RUNNING'}")

mongodb_ok = check_mongodb()
print(f"  MongoDB (localhost:27017): {'✓ RUNNING' if mongodb_ok else '✗ NOT RUNNING'}")

frontend_ok = check_frontend()
print(f"  Frontend (localhost:3002): {'✓ RUNNING' if frontend_ok else '✗ NOT RUNNING'}")

print("\n[2] SOLUTIONS...")
print("-" * 70)

if not backend_ok:
    print("\n  ✗ BACKEND NOT RUNNING")
    print("    Fix: Open PowerShell and run:")
    print("    cd BACKEND")
    print("    python app.py")
    print("\n    Then wait for: 'Running on http://127.0.0.1:5000'")

if not mongodb_ok:
    print("\n  ✗ MONGODB NOT RUNNING")
    print("    Fix: Start MongoDB service")
    print("    Windows: Services > MongoDB Server > Start")
    print("    Or: Open cmd and run: mongod.exe")
    print("    Or: Run: net start MongoDB")

if not frontend_ok and backend_ok:
    print("\n  ✗ FRONTEND NOT RUNNING")
    print("    Fix: Open PowerShell and run:")
    print("    cd FRONTEND")
    print("    npm start")
    print("\n    Then go to: http://localhost:3002")

if backend_ok and mongodb_ok:
    print("\n  ✓ ALL SERVICES OK - Running setup...")
    print("-" * 70)
    
    print("\n[3] CREATING ADMIN ACCOUNT...")
    try:
        import bcrypt
        from pymongo import MongoClient
        from datetime import datetime
        
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/dyslexia_assistant')
        db = client['dyslexia_assistant']
        users = db['users']
        
        # Hash password
        pwd_hash = bcrypt.hashpw(b'Admin@123', bcrypt.gensalt())
        
        # Delete existing admin
        users.delete_many({'email': 'admin@gmail.com'})
        
        # Create new admin
        result = users.insert_one({
            'name': 'Admin',
            'email': 'admin@gmail.com',
            'password_hash': pwd_hash,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        print(f"  ✓ Admin account created with ID: {result.inserted_id}")
        
        # Test login
        print("\n[4] TESTING LOGIN...")
        import requests
        r = requests.post(
            'http://localhost:5000/api/auth/login',
            json={'email': 'admin@gmail.com', 'password': 'Admin@123'},
            timeout=5
        )
        
        if r.status_code == 200:
            print(f"  ✓ Login test PASSED!")
            print("\n" + "="*70)
            print("✓✓✓ ADMIN SETUP COMPLETE ✓✓✓")
            print("="*70)
            print("\nYou can now log in:")
            print("  URL: http://localhost:3002")
            print("  Email: admin@gmail.com")
            print("  Password: Admin@123")
        else:
            print(f"  ✗ Login test FAILED ({r.status_code})")
            print(f"    Response: {r.text}")
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("\n1. Make sure all 3 services are running:")
print("   - Backend: python BACKEND/app.py")
print("   - MongoDB: mongod.exe or Services")
print("   - Frontend: npm start (in FRONTEND folder)")
print("\n2. Go to: http://localhost:3002")
print("\n3. Log in with:")
print("   Email: admin@gmail.com")
print("   Password: Admin@123")
print("\n4. If you get an error, tell me the EXACT message")
print("\n" + "="*70)

input("\nPress Enter to exit...")
