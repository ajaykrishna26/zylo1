import json
import urllib.request
import json as json_module

def test_pdf_upload():
    url = 'http://localhost:5000/api/pdf/upload-pdf'
    
    with open('scripts/test_sample.pdf', 'rb') as f:
        pdf_data = f.read()
    
    # Create multipart form data manually
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = []
    
    body.append(f'--{boundary}'.encode())
    body.append(b'Content-Disposition: form-data; name="pdf"; filename="test_sample.pdf"')
    body.append(b'Content-Type: application/pdf')
    body.append(b'')
    body.append(pdf_data)
    body.append(f'--{boundary}--'.encode())
    body.append(b'')
    
    body_bytes = b'\r\n'.join(body)
    
    req = urllib.request.Request(
        url,
        data=body_bytes,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json_module.loads(resp.read().decode('utf-8'))
            print('✅ PDF Upload Success!')
            print(f"Sentences extracted: {result.get('total_sentences', 0)}")
            print(f"Pages: {result.get('pages', 0)}")
            if result.get('sentences'):
                print(f"First sentence: {result['sentences'][0]['text']}")
            return True
    except Exception as e:
        print(f'❌ PDF Upload Error: {e}')
        return False

if __name__ == '__main__':
    test_pdf_upload()
