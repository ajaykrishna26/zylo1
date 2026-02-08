import json
import urllib.request

BASE = 'http://localhost:5000'

def post(path, data):
    url = BASE + path
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    reg = post('/api/auth/register', {'name': 'Debug User', 'email': 'debug_user@example.com', 'password': 'DebugPass123!'})
    print('REGISTER RESPONSE:\n', reg)
    login = post('/api/auth/login', {'email': 'debug_user@example.com', 'password': 'DebugPass123!'})
    print('LOGIN RESPONSE:\n', login)
