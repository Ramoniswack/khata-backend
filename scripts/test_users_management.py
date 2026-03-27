#!/usr/bin/env python
"""
Test script for Users Management API
Tests all CRUD operations for user management
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
USERNAME = "testreports"
PASSWORD = "test123"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('access')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_users_management():
    """Test users management functionality"""
    print("\n" + "="*80)
    print("USERS MANAGEMENT API TEST")
    print("="*80)
    
    # Get auth token
    print("\n1. Getting authentication token...")
    token = get_auth_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("✅ Authentication successful")
    
    # Test 1: List all users
    print("\n2. Listing all users...")
    response = requests.get(
        f"{BASE_URL}/auth/users/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} users")
        for user in data:
            print(f"  - {user['username']} ({user['first_name']} {user['last_name']}) - {user['role']}")
        original_count = len(data)
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # Test 2: Create a new user
    print("\n3. Creating a new user...")
    new_user_data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "supervisor",
        "phone": "9876543210",
        "password": "testpass123",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/users/",
        headers=headers,
        json=new_user_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ User created: {data['username']}")
        print(f"User ID: {data['id']}")
        print(f"Role: {data['role']}")
        print(f"Email: {data['email']}")
        print(json.dumps(data, indent=2))
        user_id = data['id']
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # Test 3: Get user details
    print(f"\n4. Getting user details for ID: {user_id}...")
    response = requests.get(
        f"{BASE_URL}/auth/users/{user_id}/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User details retrieved")
        print(f"Username: {data['username']}")
        print(f"Name: {data['first_name']} {data['last_name']}")
        print(f"Email: {data['email']}")
        print(f"Role: {data['role']}")
        print(f"Phone: {data['phone']}")
        print(f"Active: {data['is_active']}")
        print(f"Permissions: {json.dumps(data['permissions'], indent=2)}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 4: Update user
    print(f"\n5. Updating user ID: {user_id}...")
    update_data = {
        "first_name": "Updated",
        "last_name": "TestUser",
        "role": "manager",
        "phone": "1234567890"
    }
    
    response = requests.patch(
        f"{BASE_URL}/auth/users/{user_id}/",
        headers=headers,
        json=update_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User updated successfully")
        print(f"Name: {data['first_name']} {data['last_name']}")
        print(f"Role: {data['role']}")
        print(f"Phone: {data['phone']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 5: Verify the update
    print(f"\n6. Verifying the update...")
    response = requests.get(
        f"{BASE_URL}/auth/users/{user_id}/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Verification successful")
        
        if data['first_name'] == update_data['first_name']:
            print(f"✅ First name updated correctly: {data['first_name']}")
        else:
            print(f"❌ First name mismatch")
        
        if data['role'] == update_data['role']:
            print(f"✅ Role updated correctly: {data['role']}")
        else:
            print(f"❌ Role mismatch")
        
        if data['phone'] == update_data['phone']:
            print(f"✅ Phone updated correctly: {data['phone']}")
        else:
            print(f"❌ Phone mismatch")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 6: Search users
    print("\n7. Searching users by name...")
    response = requests.get(
        f"{BASE_URL}/auth/users/?search=Updated",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} users matching 'Updated'")
        for user in data:
            print(f"  - {user['username']} ({user['first_name']} {user['last_name']})")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 7: Filter by role
    print("\n8. Filtering users by role (manager)...")
    response = requests.get(
        f"{BASE_URL}/auth/users/?role=manager",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} managers")
        for user in data:
            print(f"  - {user['username']} ({user['first_name']} {user['last_name']}) - {user['role']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 8: Filter by active status
    print("\n9. Filtering active users...")
    response = requests.get(
        f"{BASE_URL}/auth/users/?is_active=true",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} active users")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 9: Update password
    print(f"\n10. Updating user password...")
    password_update = {
        "password": "newpassword123"
    }
    
    response = requests.patch(
        f"{BASE_URL}/auth/users/{user_id}/",
        headers=headers,
        json=password_update
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Password updated successfully")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 10: Deactivate user
    print(f"\n11. Deactivating user...")
    deactivate_data = {
        "is_active": False
    }
    
    response = requests.patch(
        f"{BASE_URL}/auth/users/{user_id}/",
        headers=headers,
        json=deactivate_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User deactivated")
        print(f"Active status: {data['is_active']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 11: Reactivate user
    print(f"\n12. Reactivating user...")
    reactivate_data = {
        "is_active": True
    }
    
    response = requests.patch(
        f"{BASE_URL}/auth/users/{user_id}/",
        headers=headers,
        json=reactivate_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User reactivated")
        print(f"Active status: {data['is_active']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 12: Delete user
    print(f"\n13. Deleting user ID: {user_id}...")
    response = requests.delete(
        f"{BASE_URL}/auth/users/{user_id}/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print(f"✅ User deleted successfully")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 13: Verify deletion
    print("\n14. Verifying deletion...")
    response = requests.get(
        f"{BASE_URL}/auth/users/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ User count after deletion: {len(data)}")
        if len(data) == original_count:
            print(f"✅ User count matches original ({original_count})")
        else:
            print(f"⚠️  User count: {len(data)}, expected: {original_count}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 14: Try to get deleted user (should fail)
    print(f"\n15. Trying to get deleted user (should fail)...")
    response = requests.get(
        f"{BASE_URL}/auth/users/{user_id}/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print(f"✅ Correctly returns 404 for deleted user")
    else:
        print(f"❌ Expected 404, got {response.status_code}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_users_management()
