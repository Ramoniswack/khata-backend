#!/usr/bin/env python
"""
Check tenant ownership and membership for deletion issue
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

User = get_user_model()

def check_ownership():
    """Check tenant ownership"""
    print("\n" + "="*60)
    print("CHECKING TENANT OWNERSHIP")
    print("="*60)
    
    # Find the user
    user = User.objects.filter(email='mr.bishal.baniya@gmail.com').first()
    if not user:
        print("❌ User not found")
        return
    
    print(f"\n✓ User: {user.email} (ID: {user.id})")
    print(f"  - Primary tenant: {user.tenant}")
    print(f"  - Role: {user.role}")
    
    # Find abc construction tenant
    tenant = Tenant.objects.filter(name='abc construction').first()
    if not tenant:
        print("\n❌ Tenant 'abc construction' not found")
        return
    
    print(f"\n✓ Tenant: {tenant.name} (ID: {tenant.id})")
    print(f"  - Created by: {tenant.created_by}")
    print(f"  - Created from registration: {tenant.created_from_registration}")
    print(f"  - Is active: {tenant.is_active}")
    
    # Check membership
    membership = UserTenantMembership.objects.filter(
        user=user,
        tenant=tenant
    ).first()
    
    if membership:
        print(f"\n✓ Membership exists:")
        print(f"  - Role: {membership.role}")
        print(f"  - Joined at: {membership.joined_at}")
    else:
        print(f"\n❌ No membership found")
    
    # Check all memberships for this tenant
    all_memberships = UserTenantMembership.objects.filter(tenant=tenant)
    print(f"\n📊 All memberships for this tenant: {all_memberships.count()}")
    for m in all_memberships:
        print(f"  - {m.user.email} ({m.role})")
    
    # Check deletion permission logic
    print(f"\n📊 Deletion permission check:")
    print(f"  - User is authenticated: True")
    print(f"  - User has tenant: {user.tenant is not None}")
    print(f"  - User tenant ID: {user.tenant.id if user.tenant else None}")
    print(f"  - Target tenant ID: {tenant.id}")
    print(f"  - User tenant == Target tenant: {user.tenant and user.tenant.id == tenant.id}")
    print(f"  - User is admin: {user.is_admin}")
    print(f"  - User role: {user.role}")

if __name__ == '__main__':
    check_ownership()
