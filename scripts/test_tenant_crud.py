#!/usr/bin/env python
"""
Test script for tenant CRUD operations (Create, Read, Update, Delete)
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

def print_section(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

def test_tenant_crud():
    """Test complete CRUD operations for tenants"""
    print_section("TENANT CRUD OPERATIONS TEST")
    
    # Step 1: Create a user and login
    print("\nStep 1: Creating Test User and Logging In")
    print("-" * 80)
    
    email = f"tenanttest{os.urandom(4).hex()}@example.com"
    signup_data = {
        "first_name": "Tenant",
        "last_name": "Test",
        "email": email,
        "password": "testpass123"
    }
    
    signup_response = requests.post(
        f"{BASE_URL}/api/auth/register/",
        json=signup_data
    )
    
    if signup_response.status_code != 201:
        print(f"❌ Failed to create user: {signup_response.json()}")
        return
    
    print(f"✅ User created: {email}")
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login/",
        json={"email": email, "password": "testpass123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.json()}")
        return
    
    access_token = login_response.json()['access']
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"✅ Login successful")
    
    # Step 2: Create a tenant
    print("\nStep 2: Creating Tenant")
    print("-" * 80)
    
    tenant_data = {
        "name": "Test Organization",
        "business_type": "construction",
        "owner_name": "John Doe",
        "email": "john@test.com",
        "phone": "+977 9800000000",
        "address": "Kathmandu, Nepal"
    }
    
    create_response = requests.post(
        f"{BASE_URL}/api/tenants/",
        json=tenant_data,
        headers=headers
    )
    
    print(f"Status Code: {create_response.status_code}")
    
    if create_response.status_code == 201:
        tenant = create_response.json()
        tenant_slug = tenant['slug']
        print(f"\n✅ Tenant created successfully!")
        print(f"   - ID: {tenant['id']}")
        print(f"   - Name: {tenant['name']}")
        print(f"   - Slug: {tenant_slug}")
        print(f"   - Business Type: {tenant['business_type']}")
    else:
        print(f"❌ Failed to create tenant: {create_response.json()}")
        return
    
    # Step 3: List tenants
    print("\nStep 3: Listing Tenants")
    print("-" * 80)
    
    list_response = requests.get(
        f"{BASE_URL}/api/tenants/",
        headers=headers
    )
    
    print(f"Status Code: {list_response.status_code}")
    
    if list_response.status_code == 200:
        tenants = list_response.json()
        tenant_list = tenants.get('results', tenants)
        print(f"✅ Found {len(tenant_list)} tenant(s)")
        for t in tenant_list:
            print(f"   - {t['name']} ({t['slug']})")
    else:
        print(f"❌ Failed to list tenants")
    
    # Step 4: Get tenant by slug
    print("\nStep 4: Getting Tenant by Slug")
    print("-" * 80)
    
    get_response = requests.get(
        f"{BASE_URL}/api/tenants/{tenant_slug}/",
        headers=headers
    )
    
    print(f"Status Code: {get_response.status_code}")
    
    if get_response.status_code == 200:
        tenant_detail = get_response.json()
        print(f"✅ Tenant retrieved successfully")
        print(f"   - Name: {tenant_detail['name']}")
        print(f"   - Owner: {tenant_detail['owner_name']}")
        print(f"   - Email: {tenant_detail['email']}")
    else:
        print(f"❌ Failed to get tenant: {get_response.json()}")
    
    # Step 5: Update tenant
    print("\nStep 5: Updating Tenant")
    print("-" * 80)
    
    update_data = {
        "name": "Updated Test Organization",
        "owner_name": "Jane Doe",
        "phone": "+977 9811111111"
    }
    
    update_response = requests.patch(
        f"{BASE_URL}/api/tenants/{tenant_slug}/",
        json=update_data,
        headers=headers
    )
    
    print(f"Status Code: {update_response.status_code}")
    
    if update_response.status_code == 200:
        updated_tenant = update_response.json()
        print(f"✅ Tenant updated successfully")
        print(f"   - New Name: {updated_tenant['name']}")
        print(f"   - New Owner: {updated_tenant['owner_name']}")
        print(f"   - New Phone: {updated_tenant['phone']}")
    else:
        print(f"❌ Failed to update tenant: {update_response.json()}")
    
    # Step 6: Delete tenant
    print("\nStep 6: Deleting Tenant")
    print("-" * 80)
    
    delete_response = requests.delete(
        f"{BASE_URL}/api/tenants/{tenant_slug}/",
        headers=headers
    )
    
    print(f"Status Code: {delete_response.status_code}")
    
    if delete_response.status_code == 204:
        print(f"✅ Tenant deleted successfully")
    else:
        print(f"❌ Failed to delete tenant")
        try:
            print(f"   Error: {delete_response.json()}")
        except:
            print(f"   Error: {delete_response.text}")
    
    # Step 7: Verify deletion
    print("\nStep 7: Verifying Deletion")
    print("-" * 80)
    
    verify_response = requests.get(
        f"{BASE_URL}/api/tenants/{tenant_slug}/",
        headers=headers
    )
    
    print(f"Status Code: {verify_response.status_code}")
    
    if verify_response.status_code == 404:
        print(f"✅ Tenant successfully deleted (404 Not Found)")
    else:
        print(f"❌ Tenant still exists")
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)


if __name__ == "__main__":
    try:
        test_tenant_crud()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
