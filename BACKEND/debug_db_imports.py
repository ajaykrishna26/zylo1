import sys
print("Step 0: Starting")
try:
    import os
    print("Step 1: os imported")
except:
    print("Step 1 failed")

try:
    from pymongo import MongoClient
    print("Step 2: pymongo imported")
except Exception as e:
    print(f"Step 2 failed: {e}")

try:
    from dotenv import load_dotenv
    print("Step 3: dotenv imported")
except Exception as e:
    print(f"Step 3 failed: {e}")

try:
    import certifi
    print("Step 4: certifi imported")
except Exception as e:
    print(f"Step 4 failed: {e}")

print("All imports tested successfully")
