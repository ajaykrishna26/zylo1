import requests

url = 'http://localhost:5000/api/pdf/upload-pdf'
files = {'pdf': open('scripts/test_sample.pdf','rb')}
try:
    r = requests.post(url, files=files)
    print('STATUS', r.status_code)
    print(r.text)
except Exception as e:
    print('ERROR', e)
