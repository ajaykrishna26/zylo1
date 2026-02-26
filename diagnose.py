#!/usr/bin/env python3
"""
Diagnostic script to debug admin setup
"""
import sys
import os

print("="*60)
print("DIAGNOSTIC CHECK")
print("="*60)

# Check 1: Python version
print(f"\n[1] Python: {sys.version.split()[0]}")

# Check 2: Dependencies
print(f"\n[2] Checking dependencies...")
deps = {'pymongo': False, 'bcrypt': False, 'requests': False}

try:
    import pymongo
    deps['pymongo'] = True
    print(f"    ✓ pymongo {pymongo.__version__}")
except:
    print(f"    ✗ pymongo - NOT INSTALLED")

try:
    import bcrypt
    deps['bcrypt'] = True
    print(f"    ✓ bcrypt {bcrypt.__version__}")
except:
    print(f"    ✗ bcrypt - NOT INSTALLED")

try:
    import requests
    deps['requests'] = True
    print(f"    ✓ requests {requests.__version__}")
except:
    print(f"    ✗ requests - NOT INSTALLED")

# Check 3: MongoDB Connection
print(f"\n[3] MongoDB Connection...")
try:
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/dyslexia_assistant', serverSelectionTimeoutMS=3000)
    client.server_info()
    print(f"    ✓ Connected to MongoDB")
    
    # Check 4: Can we access users collection?
    print(f"\n[4] Checking users collection...")
    db = client['dyslexia_assistant']
    users = db['users']
    count = users.count_documents({})
    print(f"    ✓ Users collection exists ({count} total users)")
    
    # Check 5: Existing admin?
    print(f"\n[5] Checking for existing admin...")
    admin = users.find_one({'email': 'admin@gmail.com'})
    if admin:
        print(f"    ✓ admin@gmail.com already exists")
    else:
        print(f"    ✗ admin@gmail.com NOT found")
    
    # Check 6: Try to create admin
    print(f"\n[6] Attempting to create admin...")
    try:
        import bcrypt
        from datetime import datetime
        
        pwd_hash = bcrypt.hashpw(b'Admin@123', bcrypt.gensalt())
        
        # Delete existing
        users.delete_many({'email': 'admin@gmail.com'})
        
        # Insert new
        result = users.insert_one({
            'name': 'Admin',
            'email': 'admin@gmail.com',
            'password_hash': pwd_hash,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        print(f"    ✓ Admin created with ID: {result.inserted_id}")
        
        # Check 7: Verify in database
        print(f"\n[7] Verifying admin in database...")
        admin = users.find_one({'email': 'admin@gmail.com'})
        if admin:
            print(f"    ✓ Admin verified in database")
            print(f"      - Email: {admin['email']}")
            print(f"      - Name: {admin['name']}")
        
        # Check 8: Test login via API
        print(f"\n[8] Testing login via API...")
        try:
            import requests
            r = requests.post(
                'http://localhost:5000/api/auth/login',
                json={'email': 'admin@gmail.com', 'password': 'Admin@123'},
                timeout=5
            )
            
            if r.status_code == 200:
                print(f"    ✓ Login successful! (200)")
                print(f"\n✓✓✓ ADMIN SETUP COMPLETE ✓✓✓")
                print(f"\nYou can now log in with:")
                print(f"  Email: admin@gmail.com")
                print(f"  Password: Admin@123")
                print(f"  URL: http://localhost:3002")
            else:
                print(f"    ✗ Login failed ({r.status_code})")
                print(f"      Response: {r.text}")
        except requests.exceptions.ConnectionError:
            print(f"    ✗ Backend not running (http://localhost:5000)")
            print(f"      Start with: python BACKEND/app.py")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            
    except Exception as e:
        print(f"    ✗ Failed to create admin: {e}")
        import traceback
        traceback.print_exc()
    
    client.close()
    
except Exception as e:
    print(f"    ✗ MongoDB connection failed: {e}")
    print(f"\n    Check:")
    print(f"    - Is MongoDB running?")
    print(f"    - Windows: Services > MongoDB > Start")
    print(f"    - Or run: mongod.exe")

print("\n" + "="*60)
input("Press Enter to continue...")
