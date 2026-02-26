import subprocess, sys, os
os.chdir(r'C:\Users\DELL\OneDrive\Pictures\Desktop\reading_assistant-ak\reading_assistant-ak')
r = subprocess.run([sys.executable, 'quick_admin.py'], capture_output=True, text=True, timeout=10)
print(r.stdout)
if r.stderr: print("ERROR:", r.stderr)
