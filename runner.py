import subprocess
import sys
import os

os.chdir(r'C:\Users\DELL\OneDrive\Pictures\Desktop\reading_assistant-ak\reading_assistant-ak')
result = subprocess.run([sys.executable, 'scripts/create_admin_account.py'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Return code:", result.returncode)
