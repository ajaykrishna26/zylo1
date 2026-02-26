from db import init_db
import os
print("Starting DB test")
db = init_db()
if db:
    print("DB Success")
else:
    print("DB Failed (caught)")
print("Done")
