import requests
import json
url='http://localhost:5000/api/auth/register'
payload={'name':'Test User','email':'testuser_py_12350@example.com','password':'password123'}
try:
    r=requests.post(url,json=payload,timeout=10)
    print(r.status_code)
    print(r.text)
except Exception as e:
    print('ERROR',e)
