import sys
print("Step 0: Starting")
try:
    import os
    print("Step 1: os imported")
except Exception as e:
    print(f"Step 1 failed: {e}")

try:
    from flask import Flask
    print("Step 2: Flask imported")
except Exception as e:
    print(f"Step 2 failed: {e}")

try:
    from docx import Document
    print("Step 3: docx imported")
except Exception as e:
    print(f"Step 3 failed: {e}")

try:
    import fitz
    print("Step 4: fitz imported")
except Exception as e:
    print(f"Step 4 failed: {e}")

try:
    import torch
    print("Step 5: torch imported")
except Exception as e:
    print(f"Step 5 failed: {e}")

try:
    from routes.online_books_routes import online_books_bp
    print("Step 12: online_books_bp imported")
except Exception as e:
    print(f"Step 12 failed: {e}")

print("Reached end of test")
