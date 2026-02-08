from db import init_db

print("Attempting to connect to MongoDB Atlas...")
db = init_db()
if db is not None:
    print("SUCCESS: Connected to database successfully!")
else:
    print("FAILURE: Could not connect to database.")
