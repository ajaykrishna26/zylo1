import json
import urllib.request

BASE = 'http://localhost:5000'

def get(path):
    url = BASE + path
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    print('Testing /api/admin/users:')
    users_resp = get('/api/admin/users')
    print(users_resp)
    print('\nTesting /api/admin/uploads:')
    uploads_resp = get('/api/admin/uploads')
    print(uploads_resp)
