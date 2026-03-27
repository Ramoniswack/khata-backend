#!/usr/bin/env python
"""Test permissions API endpoints"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.permission_models import RolePermission, initialize_tenant_permissions
from tenants.models import Tenant
import requests

User = get_user_model()

def test_permissions_api():
    """Test the permissions API"""
    
    # Get a test user
    user = User.objects.filter(email='mr.bishal.baniya@gmail.com').first()
    
    if not user:
        print("❌ User not found")
        return
    
    print(f"✓ Testing with user: {user.email}")
    print(f"  Tenant: {user.tenant.name if user.tenant else 'None'}")
    print(f"  Role: {user.role}")
    
    # Initialize permissions if needed
    if user.tenant:
        perms_count = RolePermission.objects.filter(tenant=user.tenant).count()
        print(f"  Existing permissions: {perms_count}")
        
        if perms_count == 0:
            print("  Initializing default permissions...")
            initialize_tenant_permissions(user.tenant)
            perms_count = RolePermission.objects.filter(tenant=user.tenant).count()
            print(f"  Created {perms_count} permissions")
    
    # Login to get token
    print("\n1. Logging in...")
    login_response = requests.post(
        'http://localhost:8000/api/auth/login/',
        json={'email': user.email, 'password': 'test123'}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()['access']
    print(f"✓ Login successful")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test GET permissions
    print("\n2. Getting permissions...")
    get_response = requests.get(
        'http://localhost:8000/api/auth/permissions/',
        headers=headers
    )
    
    if get_response.status_code != 200:
        print(f"❌ Get permissions failed: {get_response.status_code}")
        print(get_response.text)
        return
    
    permissions_data = get_response.json()
    print(f"✓ Got permissions successfully")
    print(f"  Roles: {list(permissions_data.keys())}")
    
    # Show sample permissions
    if 'Admin' in permissions_data:
        admin_perms = permissions_data['Admin']
        print(f"  Admin permissions count: {len(admin_perms)}")
        sample_keys = list(admin_perms.keys())[:5]
        print(f"  Sample keys: {sample_keys}")
    
    # Test UPDATE permissions
    print("\n3. Updating permissions...")
    
    # Modify one permission
    test_permissions = permissions_data.copy()
    if 'Manager' in test_permissions:
        test_permissions['Manager']['Sales-View'] = True
        test_permissions['Manager']['Sales-Create'] = True
    
    update_response = requests.post(
        'http://localhost:8000/api/auth/permissions/update/',
        headers=headers,
        json=test_permissions
    )
    
    if update_response.status_code != 200:
        print(f"❌ Update permissions failed: {update_response.status_code}")
        print(update_response.text)
        return
    
    update_data = update_response.json()
    print(f"✓ Permissions updated successfully")
    print(f"  Message: {update_data.get('message')}")
    print(f"  Updated count: {update_data.get('updated_count')}")
    
    # Verify the update
    print("\n4. Verifying update...")
    verify_response = requests.get(
        'http://localhost:8000/api/auth/permissions/',
        headers=headers
    )
    
    if verify_response.status_code == 200:
        verified_data = verify_response.json()
        if 'Manager' in verified_data:
            print(f"  Manager Sales-View: {verified_data['Manager'].get('Sales-View')}")
            print(f"  Manager Sales-Create: {verified_data['Manager'].get('Sales-Create')}")
    
    print("\n✅ All tests passed!")

if __name__ == '__main__':
    test_permissions_api()
