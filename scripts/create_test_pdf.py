from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

pdf_path = 'scripts/test_sample.pdf'
c = canvas.Canvas(pdf_path, pagesize=letter)
width, height = letter

# Write sample text
c.setFont("Helvetica", 12)
y = height - 40
lines = [
    "The Quick Brown Fox Jumps Over The Lazy Dog.",
    "This is a test document for PDF reading.",
    "It contains multiple lines of text.",
    "The app should extract and read this content.",
    "Each line can be practiced for pronunciation.",
]

for line in lines:
    c.drawString(40, y, line)
    y -= 20

c.save()
print(f"Sample PDF created at {pdf_path}")
