print("Testing imports...")
import os
print("OS imported")
from flask import Flask
print("Flask imported")
from docx import Document
print("docx imported")
import fitz
print("fitz imported")
import pdfplumber
print("pdfplumber imported")

print("Importing blueprints...")
try:
    from routes.pdf_routes import pdf_bp
    print("pdf_bp imported")
    from routes.practice_routes import practice_bp
    print("practice_bp imported")
    from routes.selection_routes import selection_bp
    print("selection_bp imported")
    from routes.auth_routes import auth_bp
    print("auth_bp imported")
    from routes.history_routes import history_bp
    print("history_bp imported")
    from routes.admin_routes import admin_bp
    print("admin_bp imported")
    from routes.online_books_routes import online_books_bp
    print("online_books_bp imported")
except Exception as e:
    print(f"Crashed during blueprint import: {e}")
    import traceback
    traceback.print_exc()

print("All imports tested.")
