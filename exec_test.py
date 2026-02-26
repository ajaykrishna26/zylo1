import os
import sys

# Change to repo root for imports to work
os.chdir(r'C:\Users\DELL\OneDrive\Pictures\Desktop\reading_assistant-ak\reading_assistant-ak')
sys.path.insert(0, os.getcwd())

# Now run the test
exec(open('test_admin_login.py').read())
