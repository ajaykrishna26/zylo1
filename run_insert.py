import subprocess
import sys
import os

result = subprocess.run(
    [sys.executable, 'insert_admin_direct.py'],
    cwd=r'C:\Users\DELL\OneDrive\Pictures\Desktop\reading_assistant-ak\reading_assistant-ak',
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
sys.exit(result.returncode)
