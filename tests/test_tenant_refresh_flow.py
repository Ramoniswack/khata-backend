#!/usr/bin/env python
"""
Test script to verify tenant creation and token refresh flow
"""
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from tenants.models import Tenant

BASE_URL = 'http://127.0.0.1:8000/api'

def test_tenant_refresh_flow():
    print("=" * 80)
    print("TESTING TENANT CREATION AND TOKEN REFRESH FLOW")
    print("=" * 80)
    
    # Step 1: Create a test user
    print("\n1. Creating test user...")
    username = f"refreshtest_{os.urandom(4).hex()}"
    password = "testpass123"
    
    # Clean up any existing user
    User.objects.filter(username=username).delete()
    
    user = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password=password,
        first_name="Refresh",
        last_name="Test",
        tenant=None  # No tenant initially
    )
    print(f"✓ Created user: {username}")
    print(f"  User has tenant: {user.tenant is not None}")
    
    # Step 2: Login and get tokens
    print("\n2. Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": username,
        "password": password
    })
    
    if response.status_code != 200:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
        return
    
    login_data = response.json()
    access_token = login_data['access']
    refresh_token = login_data['refresh']
    
    print(f"✓ Login successful")
    print(f"  User in response: {login_data.get('user', {}).get('username')}")
    print(f"  Tenant in response: {login_data.get('tenant')}")
    
    # Step 3: Get profile (should have no tenant)
    print("\n3. Getting profile (before tenant creation)...")
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    
    if response.status_code != 200:
        print(f"✗ Profile fetch failed: {response.status_code}")
        return
    
    profile_data = response.json()
    print(f"✓ Profile fetched")
    print(f"  Username: {profile_data['username']}")
    print(f"  Tenant: {profile_data.get('tenant')}")
    
    # Step 4: Create a tenant
    print("\n4. Creating tenant...")
    tenant_name = f"Test Org {os.urandom(4).hex()}"
    response = requests.post(f"{BASE_URL}/tenants/", 
        headers=headers,
        json={
            "name": tenant_name,
            "business_type": "construction"
        }
    )
    
    if response.status_code not in [200, 201]:
        print(f"✗ Tenant creation failed: {response.status_code}")
        print(response.text)
        return
    
    tenant_data = response.json()
    print(f"✓ Tenant created: {tenant_data['name']}")
    print(f"  Slug: {tenant_data.get('slug', 'N/A')}")
    
    # Step 5: Check user in database (should have tenant now)
    print("\n5. Checking user in database...")
    user.refresh_from_db()
    print(f"  User has tenant: {user.tenant is not None}")
    if user.tenant:
        print(f"  Tenant name: {user.tenant.name}")
        print(f"  User role: {user.role}")
    
    # Step 6: Get profile again with OLD token (should still show no tenant in token claims)
    print("\n6. Getting profile with OLD token...")
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    profile_data = response.json()
    print(f"  Tenant in profile: {profile_data.get('tenant')}")
    
    # Step 7: Refresh token
    print("\n7. Refreshing token...")
    response = requests.post(f"{BASE_URL}/auth/token/refresh/", json={
        "refresh": refresh_token
    })
    
    if response.status_code != 200:
        print(f"✗ Token refresh failed: {response.status_code}")
        return
    
    refresh_data = response.json()
    new_access_token = refresh_data['access']
    print(f"✓ Token refreshed")
    
    # Step 8: Get profile with NEW token
    print("\n8. Getting profile with NEW token...")
    new_headers = {'Authorization': f'Bearer {new_access_token}'}
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=new_headers)
    
    if response.status_code != 200:
        print(f"✗ Profile fetch failed: {response.status_code}")
        return
    
    new_profile_data = response.json()
    print(f"✓ Profile fetched with new token")
    print(f"  Username: {new_profile_data['username']}")
    print(f"  Tenant: {new_profile_data.get('tenant')}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"User created: ✓")
    print(f"Tenant created: ✓")
    print(f"User assigned to tenant in DB: {'✓' if user.tenant else '✗'}")
    print(f"Profile shows tenant with old token: {'✓' if profile_data.get('tenant') else '✗'}")
    print(f"Profile shows tenant with new token: {'✓' if new_profile_data.get('tenant') else '✗'}")
    
    if new_profile_data.get('tenant'):
        print(f"\n✓ SUCCESS: Token refresh correctly updates tenant information!")
    else:
        print(f"\n✗ ISSUE: Token refresh did not update tenant information")
    
    # Cleanup
    print("\n9. Cleaning up...")
    user.delete()
    Tenant.objects.filter(name=tenant_name).delete()
    print("✓ Cleanup complete")

if __name__ == '__main__':
    test_tenant_refresh_flow()
