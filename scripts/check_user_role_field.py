#!/usr/bin/env python
"""
Check user role field vs membership role
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from tenants.membership_models import UserTenantMembership

User = get_user_model()

def check_roles():
    """Check sonik's roles"""
    
    print("\n" + "="*80)
    print("CHECKING USER ROLES")
    print("="*80)
    
    try:
        user = User.objects.get(email='sonik@gmail.com')
        print(f"\n✅ User: {user.username} ({user.email})")
        print(f"   - User ID: {user.id}")
        print(f"   - Primary Tenant: {user.tenant.name if user.tenant else 'None'} (ID: {user.tenant.id if user.tenant else 'N/A'})")
        print(f"   - User.role field: {user.role}")
        
    except User.DoesNotExist:
        print("\n❌ User not found")
        return
    
    # Check all memberships
    print("\n" + "-"*80)
    print("ALL MEMBERSHIPS")
    print("-"*80)
    
    memberships = UserTenantMembership.objects.filter(user=user)
    print(f"\nFound {memberships.count()} membership(s):")
    
    for mem in memberships:
        print(f"\n  Tenant: {mem.tenant.name} (ID: {mem.tenant.id})")
        print(f"  - Role in membership: {mem.role}")
        print(f"  - Is primary tenant: {mem.tenant.id == user.tenant.id if user.tenant else False}")
    
    # Analysis
    print("\n" + "-"*80)
    print("ANALYSIS")
    print("-"*80)
    
    if user.tenant:
        primary_membership = memberships.filter(tenant=user.tenant).first()
        if primary_membership:
            print(f"\n  Primary tenant: {user.tenant.name}")
            print(f"  - User.role: {user.role}")
            print(f"  - Membership.role: {primary_membership.role}")
            
            if user.role != primary_membership.role:
                print(f"\n  ❌ MISMATCH in primary tenant!")
                print(f"     User.role should match membership.role for primary tenant")
            else:
                print(f"\n  ✅ User.role matches primary tenant membership")
    
    # Check abc construction specifically
    abc_construction = Tenant.objects.filter(name='abc construction').first()
    if abc_construction:
        abc_membership = memberships.filter(tenant=abc_construction).first()
        if abc_membership:
            print(f"\n  abc construction membership:")
            print(f"  - Role: {abc_membership.role}")
            print(f"  - Is primary: {abc_construction.id == user.tenant.id if user.tenant else False}")
            
            if abc_construction.id != user.tenant.id:
                print(f"\n  ℹ️  Note: abc construction is NOT the primary tenant")
                print(f"     User.role ({user.role}) represents role in primary tenant")
                print(f"     When viewing abc construction, should show: {abc_membership.role}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    check_roles()
