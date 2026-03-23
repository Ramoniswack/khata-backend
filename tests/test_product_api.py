"""
Test product creation via API
Run this to simulate what the frontend is doing
"""
import requests
import json

# API endpoint
url = 'http://localhost:8000/api/inventory/products/'

# Get auth token first (you need to login)
# For now, we'll test without auth to see the error

# Test payload (same as frontend sends)
payload = {
    'name': 'Test Product',
    'sku': 'TEST-PROD-001',
    'category': 1,  # Use actual category ID
    'unit': 1,  # Use actual unit ID
    'cost_price': 100.00,
    'selling_price': 150.00,
    'reorder_level': 10,
    'description': 'Test product description',
    'status': 'active'
}

print("Testing product creation...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*50 + "\n")

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print(response.text)
    
    if response.status_code == 201:
        print("\n✅ SUCCESS: Product created!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
            
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
