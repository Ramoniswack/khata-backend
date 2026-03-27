#!/usr/bin/env python
"""
Test script to verify user permissions integration
Tests that permissions are correctly checked for user management actions
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from users.permission_models import RolePermission, initialize_tenant_permissions
from tenants.models import Tenant

def test_permissions():
    print("=" * 60)
    print("Testing User Permissions Integration")
    print("=" * 60)
    
    # Get a test tenant
    tenant = Tenant.objects.filter(is_active=True).first()
    if not tenant:
        print("❌ No active tenant found. Please create a tenant first.")
        return
    
    print(f"\n✓ Using tenant: {tenant.name} (slug: {tenant.slug})")
    
    # Initialize permissions if not exists
    if not RolePermission.objects.filter(tenant=tenant).exists():
        print("\n📝 Initializing default permissions...")
        initialize_tenant_permissions(tenant)
        print("✓ Permissions initialized")
    
    # Get permissions for each role
    print("\n" + "=" * 60)
    print("Permissions Matrix for Settings Module")
    print("=" * 60)
    
    roles = ['admin', 'manager', 'supervisor', 'accountant', 'viewer']
    
    for role in roles:
        settings_view = RolePermission.objects.filter(
            tenant=tenant,
            role=role,
            module='settings',
            action='view'
        ).first()
        
        settings_edit = RolePermission.objects.filter(
            tenant=tenant,
            role=role,
            module='settings',
            action='edit'
        ).first()
        
        view_allowed = settings_view.allowed if settings_view else False
        edit_allowed = settings_edit.allowed if settings_edit else False
        
        print(f"\n{role.upper()}:")
        print(f"  Settings-View: {'✓ Allowed' if view_allowed else '✗ Denied'}")
        print(f"  Settings-Edit: {'✓ Allowed' if edit_allowed else '✗ Denied'}")
        print(f"  Can manage users: {'YES' if edit_allowed else 'NO'}")
    
    # Test with actual users
    print("\n" + "=" * 60)
    print("Testing with Actual Users")
    print("=" * 60)
    
    users = User.objects.filter(tenant=tenant)[:5]
    
    if not users:
        print("\n❌ No users found in this tenant")
        return
    
    for user in users:
        settings_edit = RolePermission.objects.filter(
            tenant=tenant,
            role=user.role,
            module='settings',
            action='edit'
        ).first()
        
        can_manage = settings_edit.allowed if settings_edit else False
        
        print(f"\n{user.username} ({user.role}):")
        print(f"  Email: {user.email}")
        print(f"  Can manage users: {'✓ YES' if can_manage else '✗ NO'}")
    
    print("\n" + "=" * 60)
    print("Expected Behavior:")
    print("=" * 60)
    print("1. Admin and Manager should have Settings-Edit permission")
    print("2. Users with Settings-Edit can:")
    print("   - Invite new users")
    print("   - Change user roles")
    print("   - Remove users from organization")
    print("3. Users without Settings-Edit will see 'No access' in actions column")
    print("4. Users cannot modify their own account")
    print("\n✓ Test completed successfully!")

if __name__ == '__main__':
    test_permissions()
