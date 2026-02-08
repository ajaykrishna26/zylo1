import sys
from pathlib import Path

# Ensure project root is on sys.path so BACKEND package imports work
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from BACKEND.db import get_users_collection


if __name__ == '__main__':
    users = list(get_users_collection().find({}, {'password_hash': 0}))
    if not users:
        print('No users found')
    else:
        for u in users:
            print(u)
