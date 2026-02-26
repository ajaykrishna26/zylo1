from docx import Document
import sys

try:
    doc = Document()
    doc.add_paragraph('Test')
    print("python-docx is working!")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
