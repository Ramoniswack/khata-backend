#!/usr/bin/env python
"""
Test script to verify users endpoint includes invited users
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
from users.models import User
from tenants.models import Tenant
from tenants.membership_models import UserTenantMembership

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


def test_users_endpoint():
    """Test that users endpoint includes both direct and membership users"""
    
    print("🔍 Testing Users Endpoint with Memberships")
    print("="*60)
    
    # Get a tenant (use City Hardware which has demo data)
    tenant = Tenant.objects.filter(name='City Hardware & Suppliers').first()
    if not tenant:
        # Fallback to any non-registration tenant
        tenant = Tenant.objects.filter(created_from_registration=False).first()
    if not tenant:
        print("❌ No tenant found")
        return
    
    print(f"\n📊 Tenant: {tenant.name}")
    
    # Count direct users
    direct_users = User.objects.filter(tenant=tenant)
    print(f"   Direct users (User.tenant): {direct_users.count()}")
    for user in direct_users:
        print(f"      - {user.email} ({user.role})")
    
    # Count membership users
    memberships = UserTenantMembership.objects.filter(tenant=tenant)
    print(f"\n   Membership users (UserTenantMembership): {memberships.count()}")
    for membership in memberships:
        print(f"      - {membership.user.email} ({membership.role})")
    
    # Get an admin user for this tenant
    admin_user = direct_users.filter(role='admin').first()
    if not admin_user:
        print("\n❌ No admin user found for this tenant")
        return
    
    print(f"\n🔐 Logging in as: {admin_user.email}")
    
    # Login
    login_response = requests.post(
        f"{API_BASE}/auth/login/",
        json={"email": admin_user.email, "password": "demo123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()['access']
    print("✅ Login successful")
    
    # Get users from API
    print(f"\n📡 Fetching users from API...")
    headers = {"Authorization": f"Bearer {token}"}
    users_response = requests.get(f"{API_BASE}/auth/users/", headers=headers)
    
    if users_response.status_code != 200:
        print(f"❌ Failed to fetch users: {users_response.status_code}")
        print(f"   Response: {users_response.text}")
        return
    
    api_users = users_response.json()
    
    # Handle paginated response
    if isinstance(api_users, dict) and 'results' in api_users:
        user_list = api_users['results']
        total_count = api_users['count']
    else:
        user_list = api_users
        total_count = len(user_list)
    
    print(f"✅ API returned {total_count} users")
    print(f"\n👥 Users from API:")
    for user in user_list:
        print(f"   - {user['email']} ({user['role']})")
    
    # Calculate expected count
    expected_count = direct_users.count() + memberships.count()
    
    # Check if counts match
    print(f"\n📊 Summary:")
    print(f"   Expected users: {expected_count}")
    print(f"   API returned: {total_count}")
    
    if total_count >= memberships.count():
        print(f"\n✅ SUCCESS: API includes membership users!")
    else:
        print(f"\n❌ ISSUE: API might be missing membership users")
        print(f"   Missing: {memberships.count() - (total_count - direct_users.count())} users")


if __name__ == "__main__":
    test_users_endpoint()
