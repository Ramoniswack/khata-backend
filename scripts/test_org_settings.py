#!/usr/bin/env python
"""
Test script for Organization Settings API
Tests getting and updating current tenant settings
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

def test_org_settings():
    """Test organization settings functionality"""
    print("\n" + "="*80)
    print("ORGANIZATION SETTINGS API TEST")
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
    
    # Test 1: Get current tenant settings
    print("\n2. Getting current tenant settings...")
    response = requests.get(
        f"{BASE_URL}/tenants/current/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Current tenant: {data['name']}")
        print(f"Business Type: {data['business_type']}")
        print(f"Owner: {data['owner_name']}")
        print(f"Email: {data['email']}")
        print(f"Phone: {data['phone']}")
        print(f"Address: {data['address']}")
        print(f"Active Modules: {', '.join(data['active_modules'])}")
        print(json.dumps(data, indent=2))
        original_data = data
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # Test 2: Update tenant settings
    print("\n3. Updating tenant settings...")
    update_data = {
        "name": original_data['name'],  # Keep same name
        "business_type": "retail",
        "owner_name": "Test Owner Updated",
        "email": "updated@example.com",
        "phone": "9876543210",
        "address": "Test Street, Test City, Test District, Test Province"
    }
    
    response = requests.patch(
        f"{BASE_URL}/tenants/update_current/",
        headers=headers,
        json=update_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Settings updated successfully")
        print(f"Business Type: {data['business_type']}")
        print(f"Owner: {data['owner_name']}")
        print(f"Email: {data['email']}")
        print(f"Phone: {data['phone']}")
        print(f"Address: {data['address']}")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # Test 3: Verify the update
    print("\n4. Verifying the update...")
    response = requests.get(
        f"{BASE_URL}/tenants/current/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Verification successful")
        
        # Check if updates were applied
        if data['business_type'] == update_data['business_type']:
            print(f"✅ Business type updated correctly: {data['business_type']}")
        else:
            print(f"❌ Business type mismatch: {data['business_type']} != {update_data['business_type']}")
        
        if data['owner_name'] == update_data['owner_name']:
            print(f"✅ Owner name updated correctly: {data['owner_name']}")
        else:
            print(f"❌ Owner name mismatch: {data['owner_name']} != {update_data['owner_name']}")
        
        if data['email'] == update_data['email']:
            print(f"✅ Email updated correctly: {data['email']}")
        else:
            print(f"❌ Email mismatch: {data['email']} != {update_data['email']}")
        
        if data['phone'] == update_data['phone']:
            print(f"✅ Phone updated correctly: {data['phone']}")
        else:
            print(f"❌ Phone mismatch: {data['phone']} != {update_data['phone']}")
        
        if data['address'] == update_data['address']:
            print(f"✅ Address updated correctly: {data['address']}")
        else:
            print(f"❌ Address mismatch: {data['address']} != {update_data['address']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 4: Restore original settings
    print("\n5. Restoring original settings...")
    restore_data = {
        "name": original_data['name'],
        "business_type": original_data['business_type'].lower() if original_data['business_type'] else 'other',
        "owner_name": original_data['owner_name'],
        "email": original_data['email'],
        "phone": original_data['phone'],
        "address": original_data['address']
    }
    
    response = requests.patch(
        f"{BASE_URL}/tenants/update_current/",
        headers=headers,
        json=restore_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Original settings restored")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 5: Test partial update (only one field)
    print("\n6. Testing partial update (only owner_name)...")
    partial_update = {
        "owner_name": "Partial Update Test"
    }
    
    response = requests.patch(
        f"{BASE_URL}/tenants/update_current/",
        headers=headers,
        json=partial_update
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Partial update successful")
        print(f"Owner Name: {data['owner_name']}")
        
        # Verify other fields weren't changed
        if data['email'] == restore_data['email']:
            print(f"✅ Other fields preserved (email: {data['email']})")
        else:
            print(f"❌ Other fields changed unexpectedly")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 6: Restore again
    print("\n7. Final restore...")
    response = requests.patch(
        f"{BASE_URL}/tenants/update_current/",
        headers=headers,
        json=restore_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Settings restored to original state")
    else:
        print(f"❌ Failed: {response.text}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_org_settings()
