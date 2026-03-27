#!/usr/bin/env python
"""
Test script for simplified signup (no organization field, auto-generated username)
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

BASE_URL = "http://localhost:8000"

def test_simplified_signup():
    """Test simplified signup with auto-generated username and tenant name"""
    print("\n" + "="*80)
    print("TESTING SIMPLIFIED SIGNUP")
    print("="*80)
    
    # Test data - only essential fields
    signup_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"testuser{os.urandom(4).hex()}@example.com",  # Random email
        "password": "testpass123",
        "phone": "+977 9800000000"
    }
    
    print("\n1. Testing Signup with Auto-Generated Fields")
    print("-" * 80)
    print(f"Request Data: {json.dumps(signup_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register/",
        json=signup_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n✅ Signup successful!")
        user_data = response.json()
        print(f"   - Username (auto-generated): {user_data.get('username')}")
        print(f"   - Email: {user_data.get('email')}")
        print(f"   - Full Name: {user_data.get('first_name')} {user_data.get('last_name')}")
        
        # Try to login with the created user
        print("\n2. Testing Login with Auto-Generated Username")
        print("-" * 80)
        
        login_data = {
            "username": user_data.get('username'),
            "password": signup_data['password']
        }
        
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("\n✅ Login successful!")
            print(f"   - Access Token: {login_result.get('access')[:50]}...")
            print(f"   - User Role: {login_result.get('user', {}).get('role')}")
            
            tenant = login_result.get('tenant')
            if tenant:
                print(f"   - Tenant Name (auto-generated): {tenant.get('name')}")
                print(f"   - Tenant Slug: {tenant.get('slug')}")
                print(f"   - Active Modules: {', '.join(tenant.get('active_modules', []))}")
        else:
            print(f"\n❌ Login failed: {login_response.json()}")
    else:
        print(f"\n❌ Signup failed: {response.json()}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)


def test_duplicate_email():
    """Test that duplicate email is properly rejected"""
    print("\n" + "="*80)
    print("TESTING DUPLICATE EMAIL VALIDATION")
    print("="*80)
    
    # Create first user
    email = f"duplicate{os.urandom(4).hex()}@example.com"
    signup_data = {
        "first_name": "First",
        "last_name": "User",
        "email": email,
        "password": "testpass123"
    }
    
    print("\n1. Creating First User")
    print("-" * 80)
    response1 = requests.post(
        f"{BASE_URL}/api/auth/register/",
        json=signup_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response1.status_code}")
    if response1.status_code == 201:
        print("✅ First user created successfully")
    
    # Try to create second user with same email
    print("\n2. Attempting to Create User with Same Email")
    print("-" * 80)
    signup_data['first_name'] = "Second"
    
    response2 = requests.post(
        f"{BASE_URL}/api/auth/register/",
        json=signup_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2)}")
    
    if response2.status_code == 400:
        print("\n✅ Duplicate email properly rejected")
    else:
        print("\n❌ Duplicate email should have been rejected")
    
    print("\n" + "="*80)


def test_username_uniqueness():
    """Test that usernames are made unique when email prefix conflicts"""
    print("\n" + "="*80)
    print("TESTING USERNAME UNIQUENESS")
    print("="*80)
    
    # Create users with same email prefix
    base_email = f"john{os.urandom(4).hex()}"
    
    users = []
    for i in range(3):
        signup_data = {
            "first_name": "John",
            "last_name": f"Doe{i}",
            "email": f"{base_email}+{i}@example.com",
            "password": "testpass123"
        }
        
        print(f"\n{i+1}. Creating User with Email: {signup_data['email']}")
        print("-" * 80)
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register/",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            user_data = response.json()
            username = user_data.get('username')
            print(f"✅ User created with username: {username}")
            users.append(username)
        else:
            print(f"❌ Failed: {response.json()}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Created {len(users)} users with unique usernames:")
    for username in users:
        print(f"  - {username}")
    
    if len(users) == len(set(users)):
        print("\n✅ All usernames are unique!")
    else:
        print("\n❌ Duplicate usernames detected!")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        test_simplified_signup()
        test_duplicate_email()
        test_username_uniqueness()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
