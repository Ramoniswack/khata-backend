#!/usr/bin/env python
"""
Test script to verify the invitation role display fix.
Tests that the API returns the correct user_role for each tenant.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from tenants.membership_models import UserTenantMembership
from tenants.serializers import TenantSerializer
from rest_framework.test import APIRequestFactory

User = get_user_model()

def test_role_display():
    """Test that TenantSerializer returns correct user_role"""
    
    print("\n" + "="*60)
    print("TESTING ROLE DISPLAY FIX")
    print("="*60)
    
    # Get sonik@gmail.com user
    try:
        sonik = User.objects.get(email='sonik@gmail.com')
        print(f"\n✓ Found user: {sonik.email}")
        print(f"  - Primary tenant: {sonik.tenant.name if sonik.tenant else 'None'}")
        print(f"  - User.role field: {sonik.role}")
    except User.DoesNotExist:
        print("\n✗ User sonik@gmail.com not found")
        return
    
    # Get abc construction tenant
    try:
        abc_construction = Tenant.objects.get(name='abc construction')
        print(f"\n✓ Found tenant: {abc_construction.name}")
    except Tenant.DoesNotExist:
        print("\n✗ Tenant 'abc construction' not found")
        return
    
    # Check membership
    try:
        membership = UserTenantMembership.objects.get(
            user=sonik,
            tenant=abc_construction
        )
        print(f"\n✓ Found membership:")
        print(f"  - User: {membership.user.email}")
        print(f"  - Tenant: {membership.tenant.name}")
        print(f"  - Role: {membership.role}")
    except UserTenantMembership.DoesNotExist:
        print("\n✗ No membership found for sonik in abc construction")
        return
    
    # Test serializer
    print("\n" + "-"*60)
    print("TESTING SERIALIZER")
    print("-"*60)
    
    # Create a mock request with sonik as the user
    factory = APIRequestFactory()
    request = factory.get('/api/tenants/')
    request.user = sonik
    
    # Serialize abc construction tenant
    serializer = TenantSerializer(abc_construction, context={'request': request})
    data = serializer.data
    
    print(f"\nSerialized data for '{abc_construction.name}':")
    print(f"  - Tenant ID: {data['id']}")
    print(f"  - Tenant name: {data['name']}")
    print(f"  - user_role field: {data.get('user_role', 'NOT PRESENT')}")
    
    # Verify the role
    expected_role = membership.role
    actual_role = data.get('user_role')
    
    print("\n" + "-"*60)
    print("VERIFICATION")
    print("-"*60)
    
    if actual_role == expected_role:
        print(f"\n✓ SUCCESS: user_role matches membership role")
        print(f"  Expected: {expected_role}")
        print(f"  Got: {actual_role}")
    else:
        print(f"\n✗ FAILED: user_role does not match")
        print(f"  Expected: {expected_role}")
        print(f"  Got: {actual_role}")
    
    # Test with sonik's own organization
    if sonik.tenant:
        print("\n" + "-"*60)
        print("TESTING WITH PRIMARY TENANT")
        print("-"*60)
        
        serializer = TenantSerializer(sonik.tenant, context={'request': request})
        data = serializer.data
        
        print(f"\nSerialized data for '{sonik.tenant.name}':")
        print(f"  - Tenant ID: {data['id']}")
        print(f"  - Tenant name: {data['name']}")
        print(f"  - user_role field: {data.get('user_role', 'NOT PRESENT')}")
        print(f"  - User.role field: {sonik.role}")
        
        if data.get('user_role') == sonik.role:
            print(f"\n✓ SUCCESS: user_role matches User.role for primary tenant")
        else:
            print(f"\n✗ FAILED: user_role does not match User.role")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_role_display()
