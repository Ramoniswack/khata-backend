import requests

try:
    # Test categories endpoint
    r = requests.get('http://localhost:8000/api/inventory/categories/')
    print(f'Categories Status: {r.status_code}')
    print(f'Content-Type: {r.headers.get("Content-Type")}')
    if r.status_code == 200:
        print(f'Response: {r.json()}')
    else:
        print(f'Error Response: {r.text[:500]}')
    
    print('\n---\n')
    
    # Test units endpoint
    r = requests.get('http://localhost:8000/api/inventory/units/')
    print(f'Units Status: {r.status_code}')
    print(f'Content-Type: {r.headers.get("Content-Type")}')
    if r.status_code == 200:
        print(f'Response: {r.json()}')
    else:
        print(f'Error Response: {r.text[:500]}')
        
except Exception as e:
    print(f'Error: {e}')
