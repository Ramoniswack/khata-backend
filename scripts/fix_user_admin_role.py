#!/usr/bin/env python
"""
Fix user role to admin for organization creators
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()

def fix_user_roles():
    print("=" * 70)
    print("FIXING USER ROLES FOR ORGANIZATION CREATORS")
    print("=" * 70)
    
    # Get all users with tenants
    users_with_tenants = User.objects.filter(tenant__isnull=False).select_related('tenant')
    
    print(f"\nFound {users_with_tenants.count()} users with tenants")
    
    fixed_count = 0
    for user in users_with_tenants:
        print(f"\n{'='*70}")
        print(f"User: {user.email}")
        print(f"Current Role: {user.role}")
        print(f"Tenant: {user.tenant.name} (slug: {user.tenant.slug})")
        print(f"Is creator: {user.tenant.created_by == user}")
        
        # If user is the creator or already admin, ensure they're admin
        if user.tenant.created_by == user or user.role == 'admin':
            if user.role != 'admin':
                print(f"⚠️  User is creator but not admin! Fixing...")
                user.role = 'admin'
                user.save()
                print(f"✅ Fixed: {user.email} is now admin")
                fixed_count += 1
            else:
                print(f"✅ User is already admin")
        else:
            print(f"ℹ️  User is not creator, role: {user.role}")
    
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Total users checked: {users_with_tenants.count()}")
    print(f"Users fixed: {fixed_count}")
    print(f"✅ All organization creators are now admins")
    
    # Show current state
    print(f"\n{'='*70}")
    print(f"CURRENT USER ROLES")
    print(f"{'='*70}")
    for user in User.objects.filter(tenant__isnull=False).select_related('tenant'):
        creator_mark = "👑" if user.tenant.created_by == user else "  "
        print(f"{creator_mark} {user.email:30} | Role: {user.role:10} | Org: {user.tenant.name}")

if __name__ == "__main__":
    fix_user_roles()
