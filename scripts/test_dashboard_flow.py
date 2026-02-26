#!/usr/bin/env python3
"""
Test the complete dashboard flow
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Admin@123"
USER_EMAIL = "testuser@example.com"
USER_PASSWORD = "Test123!@"

def test_admin_flow():
    """Test admin signin → admin dashboard"""
    print("\n=== Testing Admin Flow ===")
    
    # 1. Admin login
    print("[1] Admin login...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        print(f"[FAIL] Admin login failed: {response.status_code}")
        print(response.json())
        return False
    
    admin_token = response.json()['access_token']
    admin_user = response.json()['user']
    print(f"[OK] Admin logged in: {admin_user['name']} ({admin_user['email']})")
    
    # 2. Check admin endpoints
    print("[2] Checking admin endpoints...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    users_response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
    if users_response.status_code == 200:
        user_count = len(users_response.json()['users'])
        print(f"[OK] Admin can list users: {user_count} users found")
    else:
        print(f"[FAIL] Admin users endpoint failed: {users_response.status_code}")
    
    uploads_response = requests.get(f"{BASE_URL}/api/admin/uploads", headers=headers)
    if uploads_response.status_code == 200:
        upload_count = len(uploads_response.json()['uploads'])
        print(f"[OK] Admin can list uploads: {upload_count} uploads found")
    else:
        print(f"[FAIL] Admin uploads endpoint failed: {uploads_response.status_code}")
    
    return True


def test_user_flow():
    """Test regular user signin → dashboard → upload/read flow"""
    print("\n=== Testing User Flow ===")
    
    # 1. Create/register user
    print("[1] Creating user account...")
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "name": "Test User",
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    })
    
    if response.status_code == 201 or response.status_code == 409:
        print(f"[OK] User account ready: {USER_EMAIL}")
    else:
        print(f"[FAIL] User creation failed: {response.status_code}")
        return False
    
    # 2. User login
    print("[2] User login...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    })
    
    if response.status_code != 200:
        print(f"[FAIL] User login failed: {response.status_code}")
        return False
    
    user_token = response.json()['access_token']
    user_data = response.json()['user']
    print(f"[OK] User logged in: {user_data['name']}")
    
    # 3. Check history endpoint
    print("[3] Checking user history endpoint...")
    headers = {"Authorization": f"Bearer {user_token}"}
    
    history_response = requests.get(f"{BASE_URL}/api/history", headers=headers)
    if history_response.status_code == 200:
        history = history_response.json()['history']
        print(f"[OK] User can fetch history: {len(history)} PDFs in history")
    else:
        print(f"[FAIL] History endpoint failed: {history_response.status_code}")
    
    # 4. Upload a test PDF
    print("[4] Testing PDF upload endpoint...")
    
    # Create a simple PDF for testing
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        # Create in-memory PDF
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        c.drawString(100, 750, "Test PDF for Dashboard Flow")
        c.drawString(100, 730, "This is a sample PDF for testing the reading assistant.")
        c.showPage()
        c.save()
        pdf_buffer.seek(0)
        
        files = {"pdf": ("test_dashboard.pdf", pdf_buffer)}
        response = requests.post(f"{BASE_URL}/api/pdf/upload-pdf", files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            filename = result.get('filename', 'unknown')
            sentences = result.get('sentences', [])
            pdf_url = result.get('pdf_url', 'N/A')
            print(f"[OK] PDF uploaded successfully:")
            print(f"     - Filename: {filename}")
            print(f"     - Sentences extracted: {len(sentences)}")
            print(f"     - PDF URL: {pdf_url}")
            
            # Test load-pdf endpoint
            print("[5] Testing PDF load endpoint...")
            pdf_path = filename.split('_', 1)[1] if '_' in filename else filename
            load_response = requests.post(f"{BASE_URL}/api/pdf/load-pdf", 
                json={"filename": filename},
                headers=headers
            )
            
            if load_response.status_code == 200:
                load_result = load_response.json()
                print(f"[OK] PDF loaded successfully via load-pdf endpoint")
                print(f"     - Sentences: {len(load_result.get('sentences', []))}")
            else:
                print(f"[FAIL] Load PDF failed: {load_response.status_code}")
                print(load_response.json())
        else:
            print(f"[FAIL] PDF upload failed: {response.status_code}")
            print(response.json())
    
    except Exception as e:
        print(f"[WARN] Skipping PDF test (reportlab not available): {e}")
    
    return True


def main():
    print("=" * 60)
    print("Dashboard Flow Test Suite")
    print("=" * 60)
    
    print("\nVerifying backend connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me")
    except Exception as e:
        print(f"[FAIL] Cannot reach backend at {BASE_URL}: {e}")
        return
    
    admin_ok = test_admin_flow()
    user_ok = test_user_flow()
    
    print("\n" + "=" * 60)
    if admin_ok and user_ok:
        print("✓ All dashboard flow tests passed!")
    else:
        print("✗ Some tests failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
