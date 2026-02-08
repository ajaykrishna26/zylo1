import sys
from pathlib import Path

# Ensure project root is on sys.path so BACKEND package imports work
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from BACKEND.models.user import User

if __name__ == '__main__':
    email = 'debug_user@example.com'
    password = 'DebugPass123!'
    name = 'Debug User'
    user, error = User.create_user(email, password, name)
    if error:
        print(f'Could not create user: {error}')
    else:
        print(f'User created: {user}')
