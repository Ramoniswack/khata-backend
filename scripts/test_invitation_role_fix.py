#!/usr/bin/env python
"""
Test script to verify invitation role display fix
Tests that users show their tenant-specific role from membership, not global role
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from tenants.models import Tenant
from tenants.membership_models import UserTenantMembership
from users.serializers import UserSerializer
from django.test import RequestFactory

def test_role_display():
    print("=" * 60)
    print("Testing Invitation Role Display Fix")
    print("=" * 60)
    
    # Get a test tenant
    tenant = Tenant.objects.filter(is_active=True).first()
    if not tenant:
        print("❌ No active tenant found. Please create a tenant first.")
        return
    
    print(f"\n✓ Using tenant: {tenant.name} (slug: {tenant.slug})")
    
    # Get users with memberships in this tenant
    memberships = UserTenantMembership.objects.filter(tenant=tenant).select_related('user')
    
    if not memberships.exists():
        print("\n❌ No memberships found in this tenant")
        return
    
    print(f"\n✓ Found {memberships.count()} memberships")
    
    # Create a mock request with the tenant
    factory = RequestFactory()
    request = factory.get('/')
    request.user = memberships.first().user
    request.user.tenant = tenant
    
    print("\n" + "=" * 60)
    print("User Role Comparison")
    print("=" * 60)
    
    for membership in memberships:
        user = membership.user
        
        # Serialize the user with context
        serializer = UserSerializer(user, context={'request': request})
        serialized_role = serializer.data['role']
        
        print(f"\n{user.username} ({user.email}):")
        print(f"  Global Role (User.role): {user.role}")
        print(f"  Membership Role: {membership.role}")
        print(f"  Serialized Role (API returns): {serialized_role}")
        
        if serialized_role == membership.role:
            print(f"  ✓ CORRECT - Showing membership role")
        else:
            print(f"  ✗ WRONG - Should show '{membership.role}' but showing '{serialized_role}'")
    
    print("\n" + "=" * 60)
    print("Expected Behavior:")
    print("=" * 60)
    print("1. When listing users, API should return tenant-specific role from membership")
    print("2. If user invited as 'viewer', they should show as 'viewer' in users list")
    print("3. Global User.role is only used as fallback if no membership exists")
    print("\n✓ Test completed!")

if __name__ == '__main__':
    test_role_display()
