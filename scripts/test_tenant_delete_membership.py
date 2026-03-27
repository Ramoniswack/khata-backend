#!/usr/bin/env python
"""
Test tenant deletion with membership-based permissions
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
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

User = get_user_model()

def test_tenant_delete():
    """Test tenant deletion with membership permissions"""
    print("\n" + "="*60)
    print("TESTING TENANT DELETION WITH MEMBERSHIP PERMISSIONS")
    print("="*60)
    
    # Add testserver to ALLOWED_HOSTS
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append('testserver')
    
    # Get the user
    user = User.objects.filter(email='mr.bishal.baniya@gmail.com').first()
    if not user:
        print("❌ User not found")
        return False
    
    # Get abc construction tenant
    tenant = Tenant.objects.filter(name='abc construction').first()
    if not tenant:
        print("❌ Tenant not found")
        return False
    
    print(f"\n✓ User: {user.email}")
    print(f"  - Primary tenant: {user.tenant}")
    print(f"  - Role: {user.role}")
    
    print(f"\n✓ Tenant: {tenant.name} (ID: {tenant.id})")
    print(f"  - Created by: {tenant.created_by}")
    
    # Check membership
    membership = UserTenantMembership.objects.filter(
        user=user,
        tenant=tenant
    ).first()
    
    if membership:
        print(f"\n✓ Membership:")
        print(f"  - Role: {membership.role}")
        print(f"  - Is admin: {membership.role == 'admin'}")
    else:
        print(f"\n❌ No membership found")
        return False
    
    # Get JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Create API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Try to delete the tenant
    print(f"\n🔄 Attempting to delete tenant via API...")
    print(f"   DELETE /api/tenants/{tenant.slug}/")
    
    response = client.delete(f'/api/tenants/{tenant.slug}/')
    
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code == 204:
        print(f"✅ SUCCESS! Tenant deleted")
        
        # Verify tenant is deleted
        tenant_exists = Tenant.objects.filter(id=tenant.id).exists()
        print(f"\n📊 Verification:")
        print(f"  - Tenant exists: {tenant_exists}")
        
        # Check memberships were deleted
        memberships = UserTenantMembership.objects.filter(tenant_id=tenant.id)
        print(f"  - Remaining memberships: {memberships.count()}")
        
        return True
    else:
        print(f"❌ FAILED!")
        if hasattr(response, 'data'):
            print(f"   Error: {response.data}")
        else:
            print(f"   Content: {response.content.decode()}")
        return False

if __name__ == '__main__':
    success = test_tenant_delete()
    sys.exit(0 if success else 1)
