#!/usr/bin/env python
"""
Fix missing membership records for existing users
Creates UserTenantMembership records for users who have a tenant but no membership
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from tenants.membership_models import UserTenantMembership

def fix_missing_memberships():
    print("=" * 60)
    print("Fixing Missing Membership Records")
    print("=" * 60)
    
    # Find users who have a tenant but no membership
    users_with_tenant = User.objects.filter(tenant__isnull=False)
    
    print(f"\n✓ Found {users_with_tenant.count()} users with a tenant")
    
    fixed_count = 0
    already_have_membership = 0
    
    for user in users_with_tenant:
        # Check if membership already exists
        membership = UserTenantMembership.objects.filter(
            user=user,
            tenant=user.tenant
        ).first()
        
        if membership:
            already_have_membership += 1
            print(f"  ✓ {user.username} already has membership in {user.tenant.name}")
        else:
            # Create membership with user's current role
            UserTenantMembership.objects.create(
                user=user,
                tenant=user.tenant,
                role=user.role
            )
            fixed_count += 1
            print(f"  + Created membership for {user.username} in {user.tenant.name} as {user.role}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"Total users with tenant: {users_with_tenant.count()}")
    print(f"Already had membership: {already_have_membership}")
    print(f"Created new memberships: {fixed_count}")
    print("\n✓ Fix completed!")

if __name__ == '__main__':
    fix_missing_memberships()
