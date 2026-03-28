#!/usr/bin/env python
"""
Test sidebar permissions to verify module names are correctly matched
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
from users.permission_models import RolePermission

User = get_user_model()


def test_sidebar_permissions():
    print("=" * 60)
    print("Test Sidebar Permissions Matching")
    print("=" * 60)
    
    # Get a test user with admin role
    user = User.objects.filter(role='admin', tenant__isnull=False).first()
    
    if not user:
        print("\n❌ No admin user found with tenant")
        return
    
    print(f"\nTesting with user: {user.username}")
    print(f"Role: {user.role}")
    print(f"Tenant: {user.tenant.name}")
    
    # Get permissions for this tenant
    tenant = user.tenant
    
    # Check permissions as they would be returned by the API
    print("\n" + "=" * 60)
    print("Permissions Matrix (as returned by API)")
    print("=" * 60)
    
    permissions = RolePermission.objects.filter(tenant=tenant, role='admin', allowed=True)
    
    # Group by module
    modules = {}
    for perm in permissions:
        if perm.module not in modules:
            modules[perm.module] = []
        modules[perm.module].append(perm.action)
    
    print("\nAdmin permissions by module:")
    for module, actions in sorted(modules.items()):
        print(f"  {module}: {', '.join(actions)}")
    
    # Simulate sidebar checks
    print("\n" + "=" * 60)
    print("Simulating Sidebar Permission Checks")
    print("=" * 60)
    
    # These are the module names used in the sidebar
    sidebar_modules = ['sales', 'purchase', 'inventory', 'construction', 'accounting', 'hr', 'pos']
    
    print("\nChecking canView() for each module:")
    print("(Sidebar passes lowercase, backend stores lowercase, API returns capitalized)")
    
    for module_lowercase in sidebar_modules:
        # Check if permission exists (as stored in DB - lowercase)
        has_view_perm = RolePermission.objects.filter(
            tenant=tenant,
            role='admin',
            module=module_lowercase,
            action='view',
            allowed=True
        ).exists()
        
        # This is what the API returns (capitalized)
        module_capitalized = module_lowercase.capitalize()
        
        status = "✅ SHOW" if has_view_perm else "❌ HIDE"
        print(f"  {status} {module_capitalized} module")
        print(f"       - Sidebar passes: '{module_lowercase}'")
        print(f"       - DB stores: '{module_lowercase}'")
        print(f"       - API returns: '{module_capitalized}-View'")
        print(f"       - Frontend checks: '{module_capitalized}-View'")
        print(f"       - Permission exists: {has_view_perm}")
    
    # Show the actual permission keys that would be in the API response
    print("\n" + "=" * 60)
    print("Actual Permission Keys in API Response")
    print("=" * 60)
    
    print("\nFor Admin role:")
    admin_perms = RolePermission.objects.filter(
        tenant=tenant,
        role='admin',
        allowed=True
    ).order_by('module', 'action')
    
    # Map to API format
    api_keys = []
    for perm in admin_perms:
        module_cap = perm.module.capitalize()
        action_cap = perm.action.capitalize()
        api_key = f"{module_cap}-{action_cap}"
        api_keys.append(api_key)
    
    # Show unique keys
    unique_keys = sorted(set(api_keys))
    for key in unique_keys:
        if '-View' in key:
            print(f"  ✓ {key}")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)


if __name__ == '__main__':
    test_sidebar_permissions()
