#!/usr/bin/env python3
"""
Quick test for PDF load endpoint
"""
import requests
import json

BASE_URL = "http://localhost:5000"
TOKEN = None

# Login
print("[1] Logging in...")
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "admin@gmail.com",
    "password": "Admin@123"
})

if response.status_code != 200:
    print("Login failed:", response.json())
    exit(1)

TOKEN = response.json()['access_token']
print("[OK] Logged in")

# Get first PDF from uploads folder
import os
upload_dir = "BACKEND/static/uploads"
files = os.listdir(upload_dir)
pdf_files = [f for f in files if f.endswith('.pdf')]

if pdf_files:
    test_file = pdf_files[0]
    print(f"\n[2] Testing load-pdf with: {test_file}")
    
    response = requests.post(f"{BASE_URL}/api/pdf/load-pdf", 
        json={"filename": test_file},
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print("[OK] PDF loaded successfully!")
        print(f"    Sentences: {result['total_sentences']}")
        print(f"    Pages: {result['pages']}")
        print(f"    URL: {result['pdf_url']}")
    else:
        print("[FAIL] Error:", result)
else:
    print("No PDFs found in uploads folder")
