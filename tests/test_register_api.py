#!/usr/bin/env python
"""
Test registration API endpoint
"""
import requests
import json

url = "http://localhost:8000/api/auth/register/"

data = {
    "tenant_name": "Test API Company",
    "username": "testapiuser",
    "email": "testapi@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "API",
    "phone": "+977 9800000000"
}

print(f"Testing POST {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print()

try:
    response = requests.post(url, json=data, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 201:
        print("✓ Registration successful!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"✗ Registration failed")
        print(f"Response: {response.text}")
        
        # Try to parse as JSON
        try:
            error_data = response.json()
            print(f"\nParsed error: {json.dumps(error_data, indent=2)}")
        except:
            pass
            
except requests.exceptions.ConnectionError:
    print("✗ Connection error - is the Django server running?")
    print("Run: python manage.py runserver")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
