import requests
import json

# Login first
login_url = "http://localhost:8000/api/auth/login/"
login_data = {
    "email": "user1@test.com",
    "password": "password123"
}

print("=== Logging in ===")
response = requests.post(login_url, json=login_data)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    access_token = data.get('access')
    print(f"✓ Login successful")
    print(f"User: {data.get('user', {}).get('email')}")
    print(f"Tenant: {data.get('tenant', {}).get('name') if data.get('tenant') else 'None'}")
    
    # Test users endpoint
    print("\n=== Testing /api/auth/users/ ===")
    users_url = "http://localhost:8000/api/auth/users/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(users_url, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        users = response.json()
        print(f"✓ Success! Found {len(users)} users")
        for user in users:
            print(f"  - {user.get('email')} (role: {user.get('role')})")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text}")
else:
    print(f"✗ Login failed: {response.text}")
