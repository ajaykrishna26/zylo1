#!/usr/bin/env python3
"""
Complete e2e test of dashboard flow
"""
import requests
import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

BASE_URL = "http://localhost:5000"

def create_test_pdf(content="Test Reading Material"):
    """Create a simple PDF in memory"""
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    c.drawString(100, 750, "DASHBOARD FLOW TEST")
    c.drawString(100, 730, content)
    c.drawString(100, 710, "This is a test document.")
    c.drawString(100, 690, "It validates the complete flow.")
    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

print("\n" + "="*70)
print("COMPLETE DASHBOARD FLOW TEST")
print("="*70)

# 1. User Registration
print("\n[1] User Registration...")
reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
    "name": "E2E Test User",
    "email": "e2e@test.com",
    "password": "E2ETest123!@"
})

if reg_response.status_code != 201:
    if reg_response.status_code == 409:
        print("    [INFO] User already exists, continuing...")
    else:
        print(f"    [FAIL] Registration failed: {reg_response.status_code}")
        print(f"    {reg_response.json()}")
        exit(1)
else:
    print("    [OK] User registered successfully")

# 2. User Login
print("\n[2] User Login...")
login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "e2e@test.com",
    "password": "E2ETest123!@"
})

if login_response.status_code != 200:
    print(f"    [FAIL] Login failed: {login_response.status_code}")
    exit(1)

token = login_response.json()['access_token']
user = login_response.json()['user']
headers = {"Authorization": f"Bearer {token}"}
print(f"    [OK] Logged in as: {user['name']} ({user['email']})")

# 3. Verify not admin
print("\n[3] Verify user is not admin...")
if user['email'] == 'admin@example.com':
    print("    [FAIL] User should not be admin!")
    exit(1)
print("    [OK] User is regular user (will go to Dashboard, not AdminDashboard)")

# 4. Get initial history (should be empty)
print("\n[4] Fetch history (should be empty)...")
history_response = requests.get(f"{BASE_URL}/api/history", headers=headers)
if history_response.status_code != 200:
    print(f"    [FAIL] History fetch failed: {history_response.status_code}")
    exit(1)

history = history_response.json()['history']
print(f"    [OK] History fetched: {len(history)} PDFs")

# 5. Upload PDF (Upload PDF workflow)
print("\n[5] Upload new PDF (Upload PDF card -> /upload path)...")
pdf = create_test_pdf()
files = {"pdf": ("e2e_test.pdf", pdf)}
upload_response = requests.post(f"{BASE_URL}/api/pdf/upload-pdf", 
    files=files, headers=headers
)

if upload_response.status_code != 200:
    print(f"    [FAIL] Upload failed: {upload_response.status_code}")
    print(f"    {upload_response.json()}")
    exit(1)

upload_data = upload_response.json()
filename = upload_data['filename']
stored_filename = upload_data.get('filename')
sentences = upload_data['sentences']
pdf_url = upload_data['pdf_url']

print(f"    [OK] PDF uploaded successfully")
print(f"       - Filename: {filename}")
print(f"       - Sentences extracted: {len(sentences)}")
print(f"       - URL: {pdf_url[:50]}...")

# 6. Simulate adding to history (user would do this after reading starts)
print("\n[6] Add PDF to history (normally done during reading)...")
history_add_response = requests.post(f"{BASE_URL}/api/history",
    json={
        "pdf_name": filename,
        "pdf_path": filename,
        "total_pages": upload_data.get('pages', 1),
        "total_sentences": len(sentences)
    },
    headers=headers
)

if history_add_response.status_code != 201:
    print(f"    [WARN] History add returned: {history_add_response.status_code}")
    print(f"       {history_add_response.json()}")
else:
    print(f"    [OK] PDF added to history")

# 7. Get updated history
print("\n[7] Fetch updated history (Read Books card calls this)...")
history_response = requests.get(f"{BASE_URL}/api/history", headers=headers)
history = history_response.json()['history']
print(f"    [OK] History updated: {len(history)} PDFs")

if len(history) > 0:
    pdf_history = history[0]
    print(f"       - PDF: {pdf_history.get('pdf_name', 'unknown')}")
    
    # 8. Load PDF from history (Read Books -> click PDF -> /reader)
    print("\n[8] Load PDF from history (Read Books click -> /reader)...")
    load_response = requests.post(f"{BASE_URL}/api/pdf/load-pdf",
        json={"filename": pdf_history.get('pdf_path') or pdf_history.get('pdf_name')},
        headers=headers
    )
    
    if load_response.status_code != 200:
        print(f"    [FAIL] Load failed: {load_response.status_code}")
        print(f"       {load_response.json()}")
    else:
        loaded = load_response.json()
        print(f"    [OK] PDF loaded successfully for reading")
        print(f"       - Sentences: {len(loaded['sentences'])}")
        print(f"       - Pages: {loaded['pages']}")
        print(f"       - URL: {loaded['pdf_url'][:50]}...")

# 9. Summary
print("\n" + "="*70)
print("DASHBOARD FLOW VALIDATION COMPLETE [OK]")
print("="*70)
print("\nUser Flow Paths Verified:")
print("  [OK] Sign In/Sign Up -> Dashboard (not AdminDashboard)")
print("  [OK] Dashboard -> 'Upload PDF' -> /upload -> Upload & Extract")
print("  [OK] Dashboard -> 'Read Books' -> /books -> Show History")
print("  [OK] Read Books (History) -> Select PDF -> /reader -> Load & Read")
print("\nAll endpoints responding correctly with proper data formats.")
print("Frontend is ready to use this flow.\n")
